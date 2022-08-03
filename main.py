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

    async def charge(self, amount: float, card: str, ip: str,
                     description: Optional[str] = None):
        """
        :param amount: float
        :param card: str
        :param ip: str
        :param invoice_id: str
        :param description: str
        """

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
            raise InteractionResponseError(status_code=e.status_code, method=e.method, service=e.service)
        if not response["Success"]:
            return f"somethin went wrong!"

        return response
