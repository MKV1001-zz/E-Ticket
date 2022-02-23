import requests
from requests import Session
from requests.exceptions import HTTPError
import json
 
import os 
from random import randrange
 

 
from Crypto.PublicKey import RSA
import datetime

class customAuth:
    def __init__(self):
        self.api_key = os.environ.get("FIREBASEKEY")
        self.current_user = None
    def sign_in_with_email_and_password(self, email, password):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        self.current_user = request_object.json()
        return request_object.json()
    def send_email_verification(self, id_token):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={0}".format(self.api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"requestType": "VERIFY_EMAIL", "idToken": id_token})
        request_object = requests.post(request_ref, headers=headers, data=data)
        raise_detailed_error(request_object)
        return request_object.json()


 

def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
    except HTTPError as e:
        message =request_object.json()
        raise HTTPError(e,  message)
