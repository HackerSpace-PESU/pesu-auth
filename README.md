# pesu-auth
A simple API to authenticate PESU credentials using PESU Academy

The API is secure and protects user privacy by not storing any user credentials. It only validates credentials and returns the user's profile information.

# How to use pesu-auth

You can use the API to authenticate your PESU credentials using a simple ```POST``` request. Here is an example using Python:

```python
import requests

data = {
    'username': 'your SRN or PRN here',
    'password': 'your password here',
    'profile': False # Optional, defaults to False
    # Set to True if you want to retrieve the user's profile information
}

response = requests.post("http://localhost:5000/authenticate", json=data)
print(response.json())
```

On authentication, it returns the following parameters in a JSON object. If the authentication was successful and profile data was requested, the response's 
`profile` key will store a dictionary with a user's profile information. **On an unsuccessful sign-in, this field will not exist**.

```json
{
    "status": true,
    "profile": {
        "name": "Johnny Blaze",
        "pesu_id": "PES1201800001",
        "srn": "PES1201800001",
        "program": "Bachelor of Technology",
        "branch": "Computer Science and Engineering",
        "semester": "Sem-8",
        "section": "Section A"
    },
    "message": "Login successful.",
    "timestamp": "2023-06-18 20:57:59.979374+05:30"
}
```