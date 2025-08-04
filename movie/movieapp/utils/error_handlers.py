from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
      response = exception_handler(exc, context)
      if response is not None:
          response.data['status_code'] = response.status_code
          response.data['message'] = 'An error occurred'
      return response

class CustomError(Exception):
      def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
          self.message = message
          self.status_code = status_code
          super().__init__(self.message)