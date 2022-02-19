import requests 
from uuid import uuid4 
import io 
from PIL import Image

 
def generate_ticket(event_id):
    email =""
    code = uuid4()
    access_token = "CN8OByhqxyApFbEHnQ6IUYtA1JJV1zrV8QRrb-LOJe3IxL5of2q0gxBVMkmBea1m"
    qr_url = f"https://api.qr-code-generator.com/v1/create?access-token={access_token}"
    body = {
        
        "frame_name": "no-frame",
        "qr_code_text": code,
        "image_format": "JPG",
        "image_width": 300
    }


    res = requests.post(qr_url, data=body)    
    qr_img = Image.open(io.BytesIO(res.content))
    ticket = Image.open("media/background.jpg")

    ticket.paste(qr_img, (100,0))

    return [ticket, code]

## remember to overlay remaining details 
 