from distutils.log import error
import json 
import requests 
from requests.exceptions import HTTPError

config={
    "apiKey": "AIzaSyDQvW6ZOj4Dz6aEIRv7okqS9VsREt-EjFQ",
    "authDomain": "e-ticket-318317.firebaseapp.com",
    "projectId": "e-ticket-318317",
    "storageBucket": "e-ticket-318317.appspot.com",
    "messagingSenderId": "561354891529",
    "appId": "1:561354891529:web:57a247ad1e05a0ae5cf3d8"
}


def login_admin(email,password):
    return sign_in_with_email_and_password(email,password)

def sign_in_with_email_and_password(email, password):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(config["apiKey"])
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        request_object = requests.post(request_ref, headers=headers, data=data)
        error_check = raise_detailed_error(request_object)
        if error_check["error"]:
            return error_check["message"]
        else:
            current_user = request_object.json()
            return request_object.json()

def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
        return {"error":False,"message": request_object.text}
    except HTTPError as e:
        
        return {"error":True,"message": request_object.text}

def refresh(refresh_token):
        request_ref = "https://securetoken.googleapis.com/v1/token?key={0}".format(config['apiKey'])
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"grantType": "refresh_token", "refreshToken": refresh_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        request_object_json = request_object.json()
        # handle weirdly formatted response
        user = {
            "userId": request_object_json["user_id"],
            "idToken": request_object_json["id_token"],
            "refreshToken": request_object_json["refresh_token"]
        }
        return user
 