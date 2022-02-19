import firebase_admin
from firebase_admin import credentials
from flask import Flask 
from firebase_admin import auth

 


## initializing flask app

app = Flask(__name__)

# initializing firebase seetings
 
firebaseApp = firebase_admin.initialize_app()
user = auth.get_user_by_email('vemmaks83@gmail.com')

# ACCOUNT ( Authentication etcetra)
print(firebaseApp.name)
print(user.uid)