import hashlib
import base64
from aiohttp import TCPConnector

from abstract_client import InteractionResponseError, AbstractInteractionClient


class SimplePaymentClass(AbstractInteractionClient):
    BASE_URL = "https://api.cloudpayments.ru/"

    def __init__(self, public_id: str, api_secret: str):
        """
        :param public_id: str Get from CloudPayments
        :param api_secret: str Get from CloudPayments
        """
        super().__init__()

        self.CONNECTOR = TCPConnector()

        self.public_id = public_id
        self.api_secret = api_secret

        token = f"{self.public_id}:{self.api_secret}".encode("utf-8")

        b64str = base64.b64encode(token).decode("utf-8")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {b64str}",
        }

    async def charge(self, amount: float, card: str, ip: str, description: Optional[str] = None):
        """
        :param amount: float
        :param card: str
        :param ip: str
        :param invoice_id: str
        :param description: str
        """

        self.headers["X-Request-ID"] = self.get_idempotent_request_id(
            amount=amount, card=card
        )

        data = {
            "PublicId": self.public_id,
            "IpAddress": ip,
            "Amount": amount,
            "CardCryptogramPacket": card,
            "Currency": "RUB",
            "Description": description,

        }

        try:
            response = await self.post(
                interaction_method="charge",
                url=self.endpoint_url("payments/charge"),
                headers=self.headers,
                data=data,
            )
        except InteractionResponseError as e:
            # TODO: Need to return something
            raise InteractionResponseError(status_code=e.status_code, method=e.method, service=e.service)

        if not response["Success"]:
            return f"Something went wrong!" # TODO: Need to return something

        return response

    def get_idempotent_request_id(self, amount: float, card: str) -> str:
        _hash = hashlib.new('md5')
        _hash.update(f'{amount} {card}'.encode('utf-8'))
        return _hash.hexdigest()
