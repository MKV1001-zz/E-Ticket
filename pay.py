import requests 
import json 
paystack_key_secret ="sk_test_ab64f4d2263b6cb60e30148d471e065717f9f848"
def paystack_pay(email, amount):
    data =json.dumps({"email":email ,"amount":amount})
    url = "https://api.paystack.co/transaction/initialize"
    res = requests.post(url, data= data, headers={"Content-Type": "application/json","Authorization": f"Bearer {paystack_key_secret}"})
    return res.json()

def verify_transaction(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    res = requests.get(url,headers={"Content-Type": "application/json","Authorization": f"Bearer {paystack_key_secret}"})
    if res.content.decode("UTF-8")["status"]=="true":
        return  True
    else: 
        return  False
 