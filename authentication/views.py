from django.http import JsonResponse
from rest_framework import status

# Create your views here.
def oauth_openid_callback(request):
    # Extract the 'code' parameter from the request's query parameters.
    code = request.GET['code']

    # Create a dictionary to hold the 'code' parameter.
    params = {
        "code": code
    }

    # Return a JSON response indicating a successful authorization code generation.
    return JsonResponse({"status": status.HTTP_200_OK, "message": "Authorization Code Generated Successfully!", "results": params})
