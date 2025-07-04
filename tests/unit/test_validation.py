import pytest
from pydantic import ValidationError

from app.app import validate_input


def test_valid_input_username_prn():
    validate_input("PES1201800001", "mypassword", True, ["name", "prn"])


def test_valid_input_username_email():
    validate_input("john.doe@gmail.com", "mypassword", True, ["name", "prn"])


def test_valid_input_username_phone():
    validate_input("1234567890", "mypassword", True, ["name", "prn"])


def test_valid_input_with_fields_none():
    validate_input("PES1201800001", "mypassword", False, None)


def test_missing_username():
    with pytest.raises(ValidationError) as exc_info:
        validate_input(None, "pass", True, ["name"])
    assert "Input should be a valid string" in str(exc_info.value)


def test_non_string_username():
    with pytest.raises(ValidationError) as exc_info:
        validate_input(1234, "pass", False, None)
    assert "Input should be a valid string" in str(exc_info.value)


def test_missing_password():
    with pytest.raises(ValidationError) as exc_info:
        validate_input("user", None, False, None)
    assert "Input should be a valid string" in str(exc_info.value)


def test_profile_not_boolean():
    with pytest.raises(ValidationError) as exc_info:
        validate_input("user", "pass", "invalid_bool", None)
    assert "Input should be a valid boolean" in str(exc_info.value)


def test_fields_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        validate_input("user", "pass", False, {})
    assert "Input should be a valid list" in str(exc_info.value)


def test_fields_with_invalid_field_name():
    with pytest.raises(ValidationError) as exc_info:
        validate_input("user", "pass", True, ["not_a_field"])
    assert "Invalid field" in str(exc_info.value)
