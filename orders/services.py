import africastalking
from purchase.settings import username, api_key
africastalking.initialize(username, api_key)

default_country_code = "+254" 


def sending(phone):
    # Add the default country code to the phone number
    phone_with_country_code = default_country_code + phone

    # Set the numbers in international format
    recipients = [phone_with_country_code]

    # Set your message
    message = "Your order has been succesfuly added. Thank you for choosing us!"

    # Set your shortCode or senderId
    # sender = "55786"

    try:
        response = africastalking.SMS.send(message, recipients)
        success_message = "Your order has been succesfuly added. Thank you for choosing us!"  # Custom success message
        response_data = {
            'message': success_message,
            'SMSMessageData': response['SMSMessageData']
        }
        print(response_data)
        return response_data
    except Exception as e:
        error_message = f', we have a problem: {e}'
        return {'error': error_message}
