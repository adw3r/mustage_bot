from src import interfaces, schemas

import pytest



@pytest.mark.asyncio
async def test_api():
    resp = await interfaces.Api.test_root()

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_api_get():
    resp = await interfaces.Api.get_payments()
    print(resp.text)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_api_get_with_date():
    resp = await interfaces.Api.get_payments('03.04.2025')
    print(resp.text)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_api_get_with_wrong_date():
    resp = await interfaces.Api.get_payments('01.03.2025')
    print(resp.text)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_api_get_with_wrong_date():
    resp = await interfaces.Api.get_payments('awdpolm324p3kom4hj34o')
    print(resp.text)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_api_insert():
    payment = schemas.PaymentCreate(created_at='01.01.2023', comment='test', amount_uah='234')
    resp = await interfaces.Api.add_payment(payment)
    print(resp.text)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_api_delete():
    payment_id = 4
    resp = await interfaces.Api.delete_payment(payment_id)
    print(resp.text)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_api_patch():
    payment_id = 5
    payment = schemas.PaymentPatch(comment='test')
    resp = await interfaces.Api.patch_payment(payment_id, payment)

    assert resp.status_code == 200
