from zerobouncesdk import ZBValidateResponse, ZeroBounce


class ZeroBounceClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = ZeroBounce(api_key)

    def validate_email(self, email: str, ip_address: str) -> ZBValidateResponse:
        return self.client.validate(email, ip_address)
