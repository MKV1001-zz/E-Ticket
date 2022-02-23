from uuid import uuid4
import firebase_admin
from flask import Flask, jsonify, make_response, request, send_file
from firebase_admin import credentials, storage
import string 
import random 
import os
from PIL import Image, ImageFile
import io 
import flask 
import requests
import time
from datetime import datetime
from firebase_admin import auth
from firbase import customAuth
from db_config import conn
from pay import paystack_pay, verify_transaction
from ticket import generate_ticket
from flask_httpauth import HTTPTokenAuth
 
 


 

# initializing flask app

app = Flask(__name__)

# initializing firebase settings
cred = credentials.Certificate(os.path.join(os.getcwd(),"firebase_key.json"))
bucket_name ="e-ticket-318317.appspot.com"
firebaseApp = firebase_admin.initialize_app(cred,
    {
        'storageBucket':'e-ticket-318317.appspot.com'
    }
)
bucket = storage.bucket()
custom_auth = customAuth()

# initialising Database

db = conn()
events = db['Events']
tickets = db["Tickets"]
transactions = db["Transactions"]
users = db["Users"]

# Security
flask_auth = HTTPTokenAuth(scheme='Bearer')
@flask_auth.verify_token
def verify_token(token):
    if len(token)%4 == 0:
        try:
            decoded_token= auth.verify_id_token(token)
            uid = decoded_token['uid']
            return uid
        except Exception as e:
            return 
        
        


# ACCOUNT ( Authentication etcetra)


@app.route('/accounts/sign_up', methods=['POST'])
def email_sign_up():
    request_data = request.get_json()
    email = request_data['email']
    phone_number = request_data['phoneNo']
    password = request_data['password']
    try:
        user = auth.create_user(
            email=email,
            email_verified=False,
            phone_number=phone_number,  
            password=password
        )
        date_joined = datetime.now().strftime("%d-%m-%y")
        users.insert_one({
            "email":email,
            "phone_number":phone_number,
            "_id":user.uid,
            "date_joined":date_joined
        })

        token = auth.create_custom_token(user.uid)
        custom_auth.send_email_verification(token)
        response = make_response(
            jsonify({'status':'false','message': f'User {user.uid} has been created.', 'token': token}), 201)
        return response
    except Exception as e:
        response = make_response(jsonify({'status':'false','message': f'Error Msg:{e}'}), 401)
        return response


@app.route('/accounts/signin', methods=['POST'])
def sign_in():
    data = request.get_json()
    email = data['email']
    password = data['password']
    try:
        user = custom_auth.sign_in_with_email_and_password(email, password)
        response = make_response(
            jsonify({'message': f'user signed in ', 'data': user}), 201)
        return response
    except Exception as e:
        response = make_response(jsonify({'message': f'{e}'}), 401)
        return response


# EVENTS

@app.route("/events", methods=["Post"])
@flask_auth.login_required
def get_events():
    events_list = []
    try:
        eventSnapshot = events.find()
        for event in eventSnapshot:
            events_list.append(event)
        response = make_response(
            jsonify({'message': 'Events collected', 'data': events_list}), 201)
        return response
    except Exception as e:
        response = make_response(jsonify({'message': f'{e}'}), 401)
        return response


# PAYEMENT
@app.route("/pay", methods=['Post'])
@flask_auth.login_required
def pay_handler():
    request_data = request.get_json()
    email = auth.get_user(uid=flask_auth.current_user()).email
    amount = request_data['amount']
    event_id = request_data["event_id"]
    try:
        transaction = paystack_pay(email, amount)
        response = make_response(
            jsonify({'status': 'True', 'data': transaction['data']}), 201)
        transactions.insert_one(
            {
                "_id":transaction["data"]["reference"],
                "date": datetime.now().strftime("%d-%m-%y"),
                "user":email,
                "access-code": transaction["data"]["access_code"],
                "event_id":event_id,
                "verified":False
            }
        )
        return response
    except Exception as e:
        response = make_response(jsonify({'message': f'{e}'}), 401)
        return response

@app.route('/verify')
@flask_auth.login_required
def verify_transaction(): 
    reference = request.args.get('reference')
    user = flask_auth.current_user()
    transaction = transactions.find_one({"_id":reference})
    if verify_transaction(reference): 
        event_id = transaction["event_id"]
        transactions.update_one({"_id":reference},{'$Set':{'verified':True}})
        ticket_img, ticket_code = generate_ticket(event_id) # Work on the ticket appearance
        event = events.find_one({"_id":event_id})
        events.update_one({"_id":event_id}, {'$Set':{"tickets_left":event["tickets_left"]-1}})
        id = uuid4()
        blob = bucket.blob(f"{user}/Tickets/{id}.jpg")
        imgByteArr = io.BytesIO()
        ticket_img.save(imgByteArr, format=ticket_img.format)
        imgByteArr = imgByteArr.getvalue()
        blob.upload_from_string(imgByteArr, content_type="image/jpeg")
            
        tickets.insert_one({
            "_id":id,
            "code":ticket_code,
            "event_id":event_id,
            "owner":user,
            "verified":False
        })
        send_file(ticket_img, mimetype='image/gif', download_name=f"{id}")
    else:
        response = make_response(jsonify({'message': 'Transaction Failed','status':False}), 401)
        return response

#Tickets 
@app.route("/tickets", methods=["Post"])
@flask_auth.login_required
def get_all_tickets():
    user_tickets = []
    _tickets = tickets.find({"owner":flask_auth.current_user})
    for ticket in _tickets: 
        user_tickets.append(ticket)
    response = make_response(jsonify({'status':True,'data':user_tickets}), 201)
    return response

@app.route('/tickets/download_tickets/<ticket_id>')
@flask_auth.login_required
def download_ticket(ticket_id):
    user = flask_auth.current_user()
    blob = bucket.blob(f"{user}/Tickets/{ticket_id}.jpg")
    content =blob.download_as_string()
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    image = Image.open(io.BytesIO(content))
    return send_file(image, mimetype='image/jpeg',download_name=f"{ticket_id}.jpg")
     






########################### THE HOST API ######################################

@app.route("/")
def sign_up():
    pass

@app.route("/host/sign_in", methods=['Post'])
def host_sign_in():
    data = request.get_json()
    email = data['email']
    password = data['password']
    try:
        user = custom_auth.sign_in_with_email_and_password(email, password)
        response = make_response(
            jsonify({'message': f'user signed in ', 'data': user}), 201)
        return response
    except Exception as e:
        response = make_response(jsonify({'message': f'{e}'}), 401)
        return 
        
@app.route("/host/events")
@flask_auth.login_required
def get_host_events():
    events_list = []
    try:
        eventSnapshot = events.find({"host_id":flask_auth.current_user()})
        for event in eventSnapshot:
            events_list.append(event)
        response = make_response(
            jsonify({'message': 'Events collected', 'data': events_list, 'status':True}), 201)
        return response
    except Exception as e:
        response = make_response(jsonify({'message': f'{e}', 'status':False}), 401)
        return response

@app.route("/host/events/<event_id>", methods=['Post'])
@flask_auth.login_auth
def get_event_details(event_id):
    events_list = []
    try:
        eventSnapshot = events.find({"_id":event_id})
        for event in eventSnapshot:
            events_list.append(event)
        response = make_response(
            jsonify({'message': 'Events collected', 'data': events_list}), 201)
        return response
    except Exception as e:
        response = make_response(jsonify({'message': f'{e}'}), 401)
        return response

@app.route("/host/verify_ticket", methods=['Post'])
def verify_ticket():
    request_data = request.get_json()
    code = request_data["code"]
    event_id = request_data["event_id"]
    ticket = tickets.find({"code":code})
    if ticket["verified"]=='false':
        tickets.update_one({'_id':ticket["_id"], '$Set':{'verified':'true'}})
        if ticket['event_id']==event_id:
            message = "Ticket is vaild"
        else: 
            message="Ticket is not for this event"
        response = make_response(jsonify({'message': message }), 201)
        return response
    else:
        message="Ticket is already used"
        response = make_response(jsonify({'message': message }), 201)
        return response

@app.route("/host/create_event")
@flask_auth.login_required
def create_event():
    request_data = request.get_json()
    _id =  get_random_string(10)
    request_data['_id'] =_id
    image = request.files.get('image')
    _, ext = os.path.splitext(image.filename)
    file_bytes = image.stream

    filename = f'{_id}.{ext.lower()}'
    blob = bucket.blob(f"{flask_auth.current_user()}/Event-media/{filename}")
    blob.upload_from_string(file_bytes, content_type="image/jpeg")
    event = events.insert_one(request_data)
    response = make_response(
            jsonify({'message': f'Event id {event.inserted_id} created'}), 201)
    return response
     



def get_random_string(length):
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return result_str


if __name__ == "__main__":
    app.run(debug=True)

 


