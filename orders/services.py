import africastalking
from purchase.settings import username, api_key
africastalking.initialize(username, api_key)

def sending(phone):
        # Set the numbers in international format
        recipients = [phone]
        # Set your message
        message = "You order has been made"
        # Set your shortCode or senderId
        sender = "55786"
        try:
            response = africastalking.SMS.send(message, recipients)
            print (response)
        except Exception as e:
            print (f'Houston, we have a problem: {e}')