from rest_framework.response import Response


class ApiResponse(Response):
    """
    Standard API response.
    """

    def __init__(
        self,
        *,
        success: bool,
        message: str,
        data=None,
        errors=None,
        status_code=200,
        **kwargs,
    ):
        response = {
            "success": success,
            "message": message,
            "data": data,
            "errors": errors,
        }

        super().__init__(
            data=response,
            status=status_code,
            **kwargs,
        )