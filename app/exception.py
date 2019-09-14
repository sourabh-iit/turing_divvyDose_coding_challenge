class ValidationError(Exception):
  """ Raised when an expected error occurs in api call """
  pass

class UnExepectedError(Exception):
  """ Raised when an unexpected error occurs in api call """
  pass