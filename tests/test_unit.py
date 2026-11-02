from decimal import Decimal
from app.schemas.api import TransferRequest
from pydantic import ValidationError
import pytest
from app.core.security import hash_password, verify_password

def test_password_hash():
    h=hash_password("very-secure-password")
    assert h!="very-secure-password"
    assert verify_password("very-secure-password",h)
    assert not verify_password("wrong-password",h)

def test_amount_validation():
    with pytest.raises(ValidationError):
        TransferRequest(source_id="a",destination_id="b",amount=Decimal("-1"))
    with pytest.raises(ValidationError):
        TransferRequest(source_id="a",destination_id="b",amount=Decimal("0.001"))
