# pesu-auth

A simple API to authenticate PESU credentials using PESU Academy

The API is secure and protects user privacy by not storing any user credentials. It only validates credentials and
returns the user's profile information.

### PESUAuth LIVE Deployment

* You can access the PESUAuth API endpoint [here](https://pesu-auth.onrender.com/).
* You can view the health status of the API on the [PESUAuth Health Dashboard](https://xzlk85cp.status.cron-job.org/).

> :warning: **Warning:** The live version is hosted on a free tier server, so you might experience some latency on the
> first request since the server might not be awake. Subsequent requests will be faster.

# How to use pesu-auth

## Non-Interactive Mode

This is the most common and recommended way to use the API. You can send a request to `/authenticate` endpoint with the
user's credentials and the API will return a JSON object, with the user's profile information if requested.

### Request Parameters

| **Parameter** | **Optional** | **Type**  | **Default** | **Description**                      |
|---------------|--------------|-----------|-------------|--------------------------------------|
| `username`    | No           | `str`     |             | The user's SRN or PRN                |
| `password`    | No           | `str`     |             | The user's password                  |
| `profile`     | Yes          | `boolean` | `False`     | Whether to fetch profile information |

### Response Object

On authentication, it returns the following parameters in a JSON object. If the authentication was successful and
profile data was requested, the response's `profile` key will store a dictionary with a user's profile information.
**On an unsuccessful sign-in, this field will not exist**.

| **Field**                     | **Type**                        | **Description**                                                                             |
|-------------------------------|---------------------------------|---------------------------------------------------------------------------------------------|
| `status`                      | `boolean`                       | A flag indicating whether the overall request was successful                                |
| `profile`                     | `ProfileObject`                 | A nested map storing the profile information, returned only if requested                    |
| `know_your_class_and_section` | `KnowYourClassAndSectionObject` | A nested map storing the profile information from PESU's Know Your Class and Section Portal |
| `message`                     | `str`                           | A message that provides information corresponding to the status                             |
| `timestamp`                   | `datetime`                      | A timezone offset timestamp indicating the time of authentication                           |
| `error`                       | `str`                           | The error name and stack trace, if an application side error occurs                         |

#### Profile Object

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

#### KnowYourClassAndSectionObject

| **Field**        | **Description**                                                |
|------------------|----------------------------------------------------------------|
| `prn`            | PRN of the user                                                |
| `srn`            | SRN of the user                                                |
| `name`           | Name of the user                                               |
| `class`          | Current semester that the user is in                           |
| `section`        | Section of the user                                            |
| `cycle`          | Physics Cycle or Chemistry Cycle, if the user is in first year |
| `department`     | Abbreviation of the branch along with the campus of the user   |
| `branch`         | Abbreviation of the branch that the user is pursuing           |
| `institute_name` | The name of the campus that the user is studying in            |

<details><summary>Here is an example using Python</summary>

#### Request

```python
import requests

data = {
    'username': 'your SRN or PRN here',
    'password': 'your password here',
    'profile': False  # Optional, defaults to False
    # Set to True if you want to retrieve the user's profile information
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
    "semester": "Sem-1",
    "section": "Section A",
    "campus_code": 1,
    "campus": "RR"
  },
  "know_your_class_and_section": {
        "prn": "PES1201800001",
        "srn": "PES1201800001",
        "name": "Johnny Blaze",
        "class": "Sem-1",
        "section": "Section A",
        "cycle": "NA",
        "department": "CSE (RR Campus)",
        "branch": "CSE",
        "institute_name": "PES University (Ring Road)"
    },
  "message": "Login successful.",
  "timestamp": "2023-06-18 20:57:59.979374+05:30"
}
```

</details>

## Interactive Mode

You can also use interactive mode which will spawn a browser window and allow the user to sign in to PESU Academy. Send
a request to the `authenticateInteractive` endpoint with the `profile` query parameter set to `true` and the API will
return
a JSON object with the user's profile information.

> :warning: **Warning:** This will only work if the API is running on the same server as the client.

<details><summary>Here is an example using Python</summary>

#### Request

```python
import requests

response = requests.post("http://localhost:5000/authenticateInteractive?profile=true")
print(response.json())
```

</details>