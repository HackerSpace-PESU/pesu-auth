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

- Access the PESUAuth API endpoint [here](https://pesu-auth.onrender.com/).
- View the health status of the API on the [PESUAuth Health Dashboard](https://xzlk85cp.status.cron-job.org/).

> :warning: **Warning:** The live version is hosted on a free tier server, so you might experience some latency on the
> first request since the server might not be awake. Subsequent requests will be faster.

## How to run pesu-auth locally

Clone the repository and follow these steps to start the API locally.

### Running with Docker

This is the easiest and recommended way to run the API.

1. **Build the Docker image** from source:

   ```bash
   docker build . --tag pesu-auth
   ```

   Or **pull the pre-built image** from [Docker Hub](https://hub.docker.com/repository/docker/aditeyabaral/pesu-auth/general):

   ```bash
   docker pull aditeyabaral/pesu-auth:latest
   ```

2. **Run the Docker container**:

```bash
docker run --name pesu-auth -d -p 5000:5000 pesu-auth
# Or, if using the pre-built image:
docker run --name pesu-auth -d -p 5000:5000 aditeyabaral/pesu-auth:latest
```

3. Access the API at `http://localhost:5000/`

### Running without Docker

Requires Python 3.12 or higher.

1. Create and activate a virtual environment, then install dependencies:

#### For `conda` users:

```bash
pip install -r requirements.txt
```

#### For `uv` users:

```bash
uv sync
```

2. Run the API:

#### For `conda` users:

```bash
python -m app.app
```

#### For `uv` users:

```bash
uv run python -m app.app
```

3. Access the API at `http://localhost:5000/`

### Setting up a Development Environment

1. Install all dependencies:

#### For `conda` users:

```bash
pip install -r requirements.txt
pip install pytest pytest-cov httpx python-dotenv pre-commit
```

#### For `uv` users:

```bash
uv sync --all-extras
```

2. Set up environment variables:

```bash
cp .env.example .env
# Replace <YOUR_..._HERE> in .env with actual values
```

3. Set up pre-commit hooks:

```bash
pre-commit install
pre-commit run --all-files
```

4. Run the API using the same commands as mentioned in the previous section.

# How to use pesu-auth

Send a `POST` request to `/authenticate` with user credentials.

### Request Parameters

| Parameter  | Optional | Type        | Default | Description                                                                |
| ---------- | -------- | ----------- | ------- | -------------------------------------------------------------------------- |
| `username` | No       | `string`    |         | User's SRN or PRN                                                          |
| `password` | No       | `string`    |         | User's password                                                            |
| `profile`  | Yes      | `boolean`   | False   | Whether to fetch user profile                                              |
| `fields`   | Yes      | `list[str]` | None    | Specific profile fields to fetch. All fields are returned if not specified |

### Response Object

| Field       | Type            | Description                                                 |
| ----------- | --------------- | ----------------------------------------------------------- |
| `status`    | `boolean`       | True if authentication succeeded                            |
| `message`   | `string`        | Message indicating login result                             |
| `timestamp` | `datetime`      | ISO format timestamp of the response                        |
| `profile`   | `ProfileObject` | User profile object (only if `profile=true`)                |
| `error`     | `string`        | Error name and stack trace if application-side error occurs |

#### ProfileObject

| Field               | Description                          |
| ------------------- | ------------------------------------ |
| `name`              | Full name of the user                |
| `prn`               | PRN                                  |
| `srn`               | SRN                                  |
| `program`           | Degree program                       |
| `branch_short_code` | Abbreviated branch code              |
| `branch`            | Full branch name                     |
| `semester`          | Current semester                     |
| `section`           | User's section                       |
| `email`             | Registered email                     |
| `phone`             | Registered phone number              |
| `campus_code`       | Campus code (1 = RR, 2 = EC)         |
| `campus`            | Campus name abbreviation             |
| `error`             | Stack trace if profile parsing fails |

## Integrating with pesu-auth

### Python Example

```python
import requests

data = {
    "username": "your SRN or PRN here",
    "password": "your password here",
    "profile": True
}

response = requests.post("http://localhost:5000/authenticate", json=data)
print(response.json())
```

### cURL Example

```bash
curl -X POST http://localhost:5000/authenticate \
-H "Content-Type: application/json" \
-d '{
    "username": "your SRN or PRN here",
    "password": "your password here"
}'
```

### Example Response

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
  "timestamp": "2024-07-28T22:30:10.103368+05:30"
}
```
