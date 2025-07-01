# pesu-auth

[![Docker Image Build](https://github.com/HackerSpace-PESU/pesu-auth/actions/workflows/docker.yaml/badge.svg)](https://github.com/HackerSpace-PESU/pesu-auth/actions/workflows/docker.yml)
[![Pre-Commit Checks](https://github.com/HackerSpace-PESU/pesu-auth/actions/workflows/pre-commit.yaml/badge.svg)](https://github.com/HackerSpace-PESU/pesu-auth/actions/workflows/pre-commit.yaml)
[![Python Version Compatibility](https://github.com/HackerSpace-PESU/pesu-auth/actions/workflows/flake8.yaml/badge.svg)](https://github.com/HackerSpace-PESU/pesu-auth/actions/workflows/flake8.yml)
[![Deploy](https://github.com/HackerSpace-PESU/pesu-auth/actions/workflows/deploy.yaml/badge.svg)](https://github.com/HackerSpace-PESU/pesu-auth/actions/workflows/deploy.yaml)

![Docker Automated build](https://img.shields.io/docker/automated/aditeyabaral/pesu-auth?logo=docker)
![Docker Image Version (tag)](https://img.shields.io/docker/v/aditeyabaral/pesu-auth/latest?logo=docker&label=build%20commit)
![Docker Image Size (tag)](https://img.shields.io/docker/image-size/aditeyabaral/pesu-auth/latest?logo=docker)

A simple API to authenticate PESU credentials using PESU Academy.

The API is secure and protects user privacy by not storing any user credentials. It only validates credentials and
returns the user's profile information. No personal data is stored.

### PESUAuth LIVE Deployment

* You can access the PESUAuth API endpoint [here](https://pesu-auth.onrender.com/).
* You can view the health status of the API on the [PESUAuth Health Dashboard](https://xzlk85cp.status.cron-job.org/).

> :warning: **Warning:** The live version is hosted on a free tier server, so you might experience some latency on the
> first request since the server might not be awake. Subsequent requests will be faster.

## How to run pesu-auth locally

Running the PESUAuth API locally is simple. Clone the repository and follow the steps below to get started.

### Running with Docker

This is the easiest and recommended way to run the API locally. Ensure you have Docker installed on your system. Run the
following commands to start the API.

1. Build the Docker image either from the source code or pull the pre-built image from Docker Hub.

    1. You can build the Docker image from the source code by running the following command in the root directory of
       the repository.

   ```bash
   docker build . --tag pesu-auth
   ```

    2. You can also pull the pre-built Docker image
       from [Docker Hub](https://hub.docker.com/repository/docker/aditeyabaral/pesu-auth/general) by running the
       following command:

   ```bash
   docker pull aditeyabaral/pesu-auth:latest
   ````

2. Run the Docker container

```bash
docker run --name pesu-auth -d -p 5000:5000 pesu-auth
# If you pulled the pre-built image, use the following command instead:
docker run --name pesu-auth -d -p 5000:5000 aditeyabaral/pesu-auth:latest
```

3. Access the API at `http://localhost:5000/`

### Running without Docker

If you don't have Docker installed, you can run the API using Python. Ensure you have Python 3.10 or higher installed
on your system.

1. Create a virtual environment using `conda`, `uv` or any other virtual environment manager of your choice and activate
   it. Then, install the dependencies using the following command.

#### For `conda` users:

```bash
pip install -r requirements.txt
```

#### For `uv` users:

```bash
uv sync
```

2. Run the API using the following command.

#### For `conda` users:

```bash
python -m app.app
```

#### For `uv` users:

```bash
uv run python -m app.app
```

3. Access the API as previously mentioned.

### Setting up a Development Environment

If you want to contribute to the project, please follow these steps to set up your development environment:

1. Create a virtual environment using `conda`, `uv` or any other virtual environment manager of your choice and activate
   it. Then, install both the server and development dependencies using the following commands.

#### For `conda` users:

  ```bash
  pip install -r requirements.txt
  pip install pytest pytest-cov httpx python-dotenv pre-commit
  ```

#### For `uv` users:

   ```bash
   uv sync --all-extras
   ```

2. Set up environment variables. Copy the `.env.example` file to `.env` and replace all `<YOUR_..._HERE>` placeholders
   with your actual test user details. Each variable has been documented in the `.env.example` file for clarity.

```bash
cp .env.example .env
```

3. Set up pre-commit hooks to ensure code quality and consistency. Run the following command and then test the hooks
   using the following command.

```bash
pre-commit install
pre-commit run --all-files
```

4. Run the API using the same commands as mentioned in the previous section.

# How to use pesu-auth

You can send a request to the `/authenticate` endpoint with the user's credentials and the API will return a JSON
object,
with the user's profile information if requested.

### Request Parameters

| **Parameter** | **Optional** | **Type**    | **Default** | **Description**                                                                                 |
|---------------|--------------|-------------|-------------|-------------------------------------------------------------------------------------------------|
| `username`    | No           | `str`       |             | The user's SRN or PRN                                                                           |
| `password`    | No           | `str`       |             | The user's password                                                                             |
| `profile`     | Yes          | `boolean`   | `False`     | Whether to fetch profile information                                                            |
| `fields`      | Yes          | `list[str]` | `None`      | Which fields to fetch from the profile information. If not provided, all fields will be fetched |

### Response Object

On authentication, it returns the following parameters in a JSON object. If the authentication was successful and
profile data was requested, the response's `profile` key will store a dictionary with a user's profile information.
**On an unsuccessful sign-in, this field will not exist**.

| **Field**   | **Type**        | **Description**                                                          |
|-------------|-----------------|--------------------------------------------------------------------------|
| `status`    | `boolean`       | A flag indicating whether the overall request was successful             |
| `profile`   | `ProfileObject` | A nested map storing the profile information, returned only if requested |
| `message`   | `str`           | A message that provides information corresponding to the status          |
| `timestamp` | `datetime`      | A timezone offset timestamp indicating the time of authentication        |
| `error`     | `str`           | The error name and stack trace, if an application side error occurs      |#### Profile Ob    ject

#### `ProfileObject`

This object contains the user's profile information, which is returned only if the `profile` parameter is set to `True`.
If the authentication fails, this field will not be present in the response.

| **Field**           | **Description**                                        |
|---------------------|--------------------------------------------------------|
| `name`              | Name of the user                                       |
| `prn`               | PRN of the user                                        |
| `srn`               | SRN of the user                                        |
| `program`           | Academic program that the user is enrolled into        |
| `branch_short_code` | Abbreviation of the branch that the user is pursuing   |
| `branch`            | Complete name of the branch that the user is pursuing  |
| `semester`          | Current semester that the user is in                   |
| `section`           | Section of the user                                    |
| `email`             | Email address of the user registered with PESU         |
| `phone`             | Phone number of the user registered with PESU          |
| `campus_code`       | The integer code of the campus (1 for RR and 2 for EC) |
| `campus`            | Abbreviation of the user's campus name                 |
| `error`             | The error name and stack trace, if an error occurs     |

## Integrating your application with pesu-auth

Here are some examples of how you can integrate your application with the PESUAuth API using Python and cURL.

### Python

#### Request

```python
import requests

data = {
    "username": "your SRN or PRN here",
    "password": "your password here",
    "profile": True,  # Optional, defaults to False
}

response = requests.post("http://localhost:5000/authenticate", json=data)
print(response.json())
```

#### Response

```json
{
  "status": true,
  "profile": {
    "name": "Johnny Blaze",
    "prn": "PES1201800001",
    "srn": "PES1201800001",
    "program": "Bachelor of Technology",
    "branch_short_code": "CSE",
    "branch": "Computer Science and Engineering",
    "semester": "NA",
    "section": "NA",
    "email": "johnnyblaze@gmail.com",
    "phone": "1234567890",
    "campus_code": 1,
    "campus": "RR"
  },
  "message": "Login successful.",
  "timestamp": "2024-07-28 22:30:10.103368+05:30"
}
```

### cURL

#### Request

```bash
curl -X POST http://localhost:5000/authenticate \
-H "Content-Type: application/json" \
-d '{
    "username": "your SRN or PRN here",
    "password": "your password here"
}'
```

#### Response

```json
{
  "status": true,
  "message": "Login successful.",
  "timestamp": "2024-07-28 22:30:10.103368+05:30"
}
```

## Input Validation with Pydantic

PESUAuth uses [Pydantic](https://pydantic.dev/) for robust input validation and data parsing. This ensures that all API requests are properly validated before processing, providing clear error messages for invalid inputs.

### Validation Model

All requests to the `/authenticate` endpoint are validated using the `ValidateInputModel` Pydantic model with the following features:

- **Strict type checking**: Prevents automatic type coercion (e.g., string "true" won't be converted to boolean)
- **Custom field validation**: Each field has specific validation rules
- **Automatic error handling**: Returns descriptive error messages for validation failures

### Validation Rules

| **Field**  | **Type**           | **Validation Rules**                                                               |
|------------|-------------------|-------------------------------------------------------------------------------------|
| `username` | `str`             | Cannot be empty or whitespace-only; automatically trimmed                          |
| `password` | `str`             | Cannot be empty                                                                     |
| `profile`  | `bool`            | Must be a boolean value (strict - strings like "true" will be rejected)           |
| `fields`   | `Optional[list[str]]` | Must be a non-empty list or None; all field names must be from predefined allowed list |

### Allowed Profile Fields

When using the `fields` parameter, only the following field names are accepted:

```python
["name", "prn", "srn", "program", "branch_short_code", "branch", 
 "semester", "section", "email", "phone", "campus_code", "campus"]
```

### Validation Error Examples

#### Missing Required Field
```json
{
  "status": false,
  "message": "Could not validate request data: 1 validation error for ValidateInputModel\nusername\n  Field required [type=missing, input_value={'password': 'test123'}, input_type=dict]",
  "timestamp": "2024-07-01 10:30:15.123456+05:30"
}
```

#### Invalid Field Type
```json
{
  "status": false,
  "message": "Could not validate request data: 1 validation error for ValidateInputModel\nprofile\n  Input should be a valid boolean [type=bool_type, input_value='true', input_type=str]",
  "timestamp": "2024-07-01 10:30:15.123456+05:30"
}
```

#### Invalid Profile Field
```json
{
  "status": false,
  "message": "Could not validate request data: 1 validation error for ValidateInputModel\nfields\n  Value error, Invalid field: 'invalid_field'. Valid fields are: ['name', 'prn', 'srn', 'program', 'branch_short_code', 'branch', 'semester', 'section', 'email', 'phone', 'campus_code', 'campus']",
  "timestamp": "2024-07-01 10:30:15.123456+05:30"
}
```

### For Developers

The validation model is defined in `models/validate_input_model.py` and can be imported for testing or integration:

```python
from models.validate_input_model import ValidateInputModel

# Example usage
try:
    validated_data = ValidateInputModel(
        username="PES1UG20CS123",
        password="mypassword",
        profile=True,
        fields=["name", "prn", "branch"]
    )
    print(f"Validated username: {validated_data.username}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

This approach ensures data integrity and provides clear feedback when requests don't meet the expected format.
