# import requests
# import json


# url = "https://d7-verify.p.rapidapi.com/send"
# headers = {
#     'x-rapidapi-host': "d7-verify.p.rapidapi.com",
#     'x-rapidapi-key': "ZaaQtXo6kcmsh7n67b5fTAmc7vrfp1vJpz2jsnYXRFg2gUK819",
#     'authorization': "Token 013417d9348ce94669ba6250831bb5a29b503257",
#     'content-type': "application/json",
#     'accept': "application/json"
# }


# def send(number):
#     payload = {
#         "mobile": number,
#         "sender_id": "Veloce",
#         "message": "Your Veloce OTP code is {code}",
#         "expiry": 900
#     }
#     response = requests.post(url, data=json.dumps(payload), headers=headers)
#     print(response.text)

# def resend(otp_id):


# # def resend(number):


# send("+916352095960")
# resend("1019715b-4ec8-4f0f-a514-6ab579616366")
