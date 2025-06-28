import pytest

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
    with pytest.raises(AssertionError, match="Username not provided."):
        validate_input(None, "pass", True, ["name"])


def test_non_string_username():
    with pytest.raises(AssertionError, match="Username should be a string."):
        validate_input(1234, "pass", False, None)


def test_missing_password():
    with pytest.raises(AssertionError, match="Password not provided."):
        validate_input("user", None, False, None)


def test_profile_not_boolean():
    with pytest.raises(AssertionError, match="Profile should be a boolean."):
        validate_input("user", "pass", "yes", None)


def test_fields_invalid_type():
    with pytest.raises(
        AssertionError, match="Fields should be a non-empty list or None."
    ):
        validate_input("user", "pass", False, {})


def test_fields_with_invalid_field_name():
    with pytest.raises(AssertionError) as e:
        validate_input("user", "pass", True, ["not_a_field"])
    assert "Invalid field" in str(e.value)
