import httpx

from src import schemas
from src.config import API_ENDPOINT_URI

class Api:
    URI = API_ENDPOINT_URI
    __cli = httpx.AsyncClient()

    @classmethod
    async def get_payment_by_id(cls, payment_id):
        response = await cls._make_request(f'payments/{payment_id}', 'get')
        return response

    @classmethod
    async def _make_request(cls, path, method, *args, **kwargs) -> httpx.Response:
        url = f'{cls.URI}/{path}'
        response = await cls.__cli.request(method=method, url=url, follow_redirects=True, *args, **kwargs)
        return response

    @classmethod
    async def test_root(cls) -> httpx.Response:
        response = await cls._make_request('test', 'get')
        return response

    @classmethod
    async def get_payments(cls, created_at: str | None = None):
        """
        path = URI/payments
        :param:
        :return:
        """
        params = None
        if created_at:
            params = {
                'created_at': created_at
            }
        response = await cls._make_request('payments/', 'get', params=params)
        return response

    @classmethod
    async def get_payments_with_dates(cls, get_payments_obj: schemas.GetPayments) -> httpx.Response:
        """
        path = URI/payments
        :param:
        :return:
        """
        params = {
            'created_at': get_payments_obj.created_at_first,
            'up_to_created_at': get_payments_obj.created_at_second
        }
        response = await cls._make_request('payments/', 'get', params=params)
        return response

    @classmethod
    async def add_payment(cls, payment: schemas.PaymentCreate) -> httpx.Response:
        """
        path = URI/payments/{payment_id}
        :return: httpx.Response
        """
        params = payment.model_dump()
        response = await cls._make_request(
            "payments/", "post", json=params
        )
        return response

    @classmethod
    async def delete_payment(cls, payment_id: str | int) -> httpx.Response:
        """
        path = URI/payments/{payment_id}
        :return: httpx.Response
        """
        response = await cls._make_request(
            f"payments/{payment_id}", "delete"
        )
        return response

    @classmethod
    async def patch_payment(cls, payment: schemas.PaymentPatch) -> httpx.Response:
        """
        path = URI/payments/{payment_id}
        :return: httpx.Response
        """
        data = payment.model_dump()

        response = await cls._make_request(
            f"payments/{payment.payment_id}", "patch", json=data
        )
        return response
