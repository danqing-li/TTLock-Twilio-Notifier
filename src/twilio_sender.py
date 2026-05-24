import os
from twilio.rest import Client

class TwilioSender:
    def __init__(self):
        self.client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"],
        )
        self.whatsapp_from = os.environ.get("TWILIO_WHATSAPP_FROM")
        self.sms_from = os.environ.get("TWILIO_SMS_FROM")

    def send_whatsapp(self, to, body):
        if not self.whatsapp_from:
            raise ValueError("TWILIO_WHATSAPP_FROM is required")
        return self.client.messages.create(
            body=body,
            from_=f"whatsapp:{self.whatsapp_from}",
            to=f"whatsapp:{to}",
        )

    def send_sms(self, to, body):
        if not self.sms_from:
            raise ValueError("TWILIO_SMS_FROM is required")
        return self.client.messages.create(
            body=body,
            from_=self.sms_from,
            to=to,
        )
    
# Demo
# import os
# from twilio.rest import Client

# class TwilioSender:
#     def __init__(self):
#         self.client = Client(
#             os.environ["TWILIO_ACCOUNT_SID"],
#             os.environ["TWILIO_AUTH_TOKEN"],
#         )
#         self.whatsapp_from = os.environ.get("TWILIO_WHATSAPP_FROM")
#         self.sms_from = os.environ.get("TWILIO_SMS_FROM")

#     def send_whatsapp(self, to, body):
#         if not self.whatsapp_from:
#             raise ValueError("TWILIO_WHATSAPP_FROM is required")
#         return self.client.messages.create(
#             body=body,
#             from_=f"whatsapp:{self.whatsapp_from}",
#             to=f"whatsapp:{to}",
#         )

#     def send_sms(self, to, body):
#         if not self.sms_from:
#             raise ValueError("TWILIO_SMS_FROM is required")
#         return self.client.messages.create(
#             body=body,
#             from_=self.sms_from,
#             to=to,
#         )