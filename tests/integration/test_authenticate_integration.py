import os

import pytest

from app.app import app


@pytest.fixture(scope="module")
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.mark.secret_required
def test_integration_authenticate_success(client):
    payload = {
        "username": os.getenv("TEST_PRN"),
        "password": os.getenv("TEST_PASSWORD"),
        "profile": False,
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] is True
    assert "profile" not in data
    assert "timestamp" in data
    assert data["message"] == "Login successful."


@pytest.mark.secret_required
def test_integration_authenticate_with_specific_profile_fields(client):
    username = os.getenv("TEST_PRN")
    password = os.getenv("TEST_PASSWORD")
    branch = os.getenv("TEST_BRANCH")
    branch_short_code = os.getenv("TEST_BRANCH_SHORT_CODE")
    campus = os.getenv("TEST_CAMPUS")
    assert username is not None, "TEST_PRN environment variable not set"
    assert password is not None, "TEST_PASSWORD environment variable not set"
    assert branch is not None, "TEST_BRANCH environment variable not set"
    assert branch_short_code is not None, (
        "TEST_BRANCH_SHORT_CODE environment variable not set"
    )
    assert campus is not None, "TEST_CAMPUS environment variable not set"

    expected_fields = ["prn", "branch", "branch_short_code", "campus"]
    payload = {
        "username": os.getenv("TEST_PRN"),
        "password": os.getenv("TEST_PASSWORD"),
        "profile": True,
        "fields": expected_fields,
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] is True
    assert "timestamp" in data
    assert data["message"] == "Login successful."
    assert "profile" in data
    profile = data["profile"]
    assert len(profile) == len(expected_fields), (
        f"Expected {len(expected_fields)} fields in profile, got {len(profile)}"
    )

    assert profile["prn"] == username
    assert profile["branch"] == branch
    assert profile["branch_short_code"] == branch_short_code
    assert profile["campus"] == campus
    assert "name" not in profile


@pytest.mark.secret_required
def test_integration_authenticate_with_all_profile_fields(client):
    name = os.getenv("TEST_NAME")
    username = os.getenv("TEST_PRN")
    password = os.getenv("TEST_PASSWORD")
    srn = os.getenv("TEST_SRN")
    program = os.getenv("TEST_PROGRAM")
    semester = os.getenv("TEST_SEMESTER")
    section = os.getenv("TEST_SECTION")
    email = os.getenv("TEST_EMAIL")
    phone = os.getenv("TEST_PHONE")
    campus_code = int(os.getenv("TEST_CAMPUS_CODE"))
    branch = os.getenv("TEST_BRANCH")
    branch_short_code = os.getenv("TEST_BRANCH_SHORT_CODE")
    campus = os.getenv("TEST_CAMPUS")
    # _class = os.getenv("TEST_CLASS")
    # cycle = os.getenv("TEST_CYCLE")
    # department = os.getenv("TEST_DEPARTMENT")
    # institute_name = os.getenv("TEST_INSTITUTE_NAME")

    assert name is not None, "TEST_NAME environment variable not set"
    assert username is not None, "TEST_PRN environment variable not set"
    assert password is not None, "TEST_PASSWORD environment variable not set"
    assert branch is not None, "TEST_BRANCH environment variable not set"
    assert branch_short_code is not None, (
        "TEST_BRANCH_SHORT_CODE environment variable not set"
    )
    assert campus is not None, "TEST_CAMPUS environment variable not set"
    assert srn is not None, "TEST_SRN environment variable not set"
    assert program is not None, "TEST_PROGRAM environment variable not set"
    assert semester is not None, "TEST_SEMESTER environment variable not set"
    assert section is not None, "TEST_SECTION environment variable not set"
    assert email is not None, "TEST_EMAIL environment variable not set"
    assert phone is not None, "TEST_PHONE environment variable not set"
    assert campus_code is not None, "TEST_CAMPUS_CODE environment variable not set"
    # assert _class is not None, "TEST_CLASS environment variable not set"
    # assert cycle is not None, "TEST_CYCLE environment variable not set"
    # assert department is not None, "TEST_DEPARTMENT environment variable not set"
    # assert (
    #     institute_name is not None
    # ), "TEST_INSTITUTE_NAME environment variable not set"

    all_fields = [
        "name",
        "prn",
        "srn",
        "program",
        "branch_short_code",
        "branch",
        "semester",
        "section",
        "email",
        "phone",
        "campus_code",
        "campus",
        # "class", # TODO: These fields seem to have been deprecated in the latest version
        # "cycle", # TODO: These fields seem to have been deprecated in the latest version
        # "department", # TODO: These fields seem to have been deprecated in the latest version
        # "institute_name", # TODO: These fields seem to have been deprecated in the latest version
    ]

    payload = {
        "username": username,
        "password": password,
        "profile": True,
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] is True
    assert "timestamp" in data
    assert data["message"] == "Login successful."
    assert "profile" in data
    profile = data["profile"]
    assert len(profile) == len(all_fields), (
        f"Expected {len(all_fields)} fields in profile, got {len(profile)}"
    )

    assert profile["name"] == name
    assert profile["prn"] == username
    assert profile["srn"] == srn
    assert profile["program"] == program
    assert profile["branch_short_code"] == branch_short_code
    assert profile["branch"] == branch
    assert profile["semester"] == semester
    assert profile["section"] == section
    assert profile["email"] == email
    assert profile["phone"] == phone
    assert profile["campus_code"] == campus_code
    assert profile["campus"] == campus
    # assert profile["class"] == _class
    # assert profile["cycle"] == cycle
    # assert profile["department"] == department
    # assert profile["institute_name"] == institute_name


def test_integration_invalid_password(client):
    payload = {
        "username": "INVALID_USER",
        "password": "wrongpass",
        "profile": True,
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code in (200, 500)
    data = response.get_json()
    assert data["status"] is False
    assert "Invalid" in data["message"] or "error" in data["message"].lower()


def test_integration_missing_username(client):
    payload = {
        "password": os.getenv("TEST_PASSWORD"),
        "profile": True,
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] is False
    assert "username" in data["message"].lower()


def test_integration_missing_password(client):
    payload = {
        "username": os.getenv("TEST_PRN"),
        "profile": True,
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] is False
    assert "password" in data["message"].lower()


def test_integration_username_wrong_type(client):
    payload = {
        "username": 12345,  # not a string
        "password": os.getenv("TEST_PASSWORD"),
        "profile": True,
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] is False
    assert "username" in data["message"].lower()
    assert "string" in data["message"].lower()


def test_integration_password_wrong_type(client):
    payload = {
        "username": os.getenv("TEST_PRN"),
        "password": 12345,
        "profile": True,
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] is False
    assert "password" in data["message"].lower()
    assert "string" in data["message"].lower()


def test_integration_profile_wrong_type(client):
    payload = {
        "username": os.getenv("TEST_PRN"),
        "password": os.getenv("TEST_PASSWORD"),
        "profile": "true",
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] is False
    assert "profile" in data["message"].lower()
    assert "boolean" in data["message"].lower()


def test_integration_fields_wrong_type(client):
    payload = {
        "username": os.getenv("TEST_PRN"),
        "password": os.getenv("TEST_PASSWORD"),
        "profile": True,
        "fields": "prn,branch",
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] is False
    assert "fields" in data["message"].lower()
    assert "list" in data["message"].lower()


def test_integration_fields_empty_list(client):
    payload = {
        "username": os.getenv("TEST_PRN"),
        "password": os.getenv("TEST_PASSWORD"),
        "profile": True,
        "fields": [],
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] is False
    assert "fields" in data["message"].lower()
    assert "non-empty" in data["message"].lower()


def test_integration_fields_invalid_field(client):
    payload = {
        "username": os.getenv("TEST_PRN"),
        "password": os.getenv("TEST_PASSWORD"),
        "profile": True,
        "fields": ["invalid_field"],
    }

    response = client.post("/authenticate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] is False
    assert "invalid_field" in data["message"].lower()
    assert "valid fields" in data["message"].lower()


def test_integration_readme_route(client):
    response = client.get("/readme")
    assert response.status_code == 200
    assert "html" in response.content_type
