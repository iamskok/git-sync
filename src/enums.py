from enum import Enum, unique


@unique
class HttpStatusCode(Enum):

    """ Http Status Code Enum.

    Example usage:
      HttpStatusCode.OK.value  # 200
    """

    # SUCCESSFUL RESPONSES (200–299)
    OK = 200
    CREATED = 201

    # CLIENT ERRORS (400–499)
    BAD_REQUEST = 400
    NOT_FOUND = 404
    UNPROCESSABLE_ENTITY = 422
