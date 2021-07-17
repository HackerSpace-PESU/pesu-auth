# pesu-auth
A simple API to authenticate PESU credentials using PESU Academy

The API is secure and protects user privacy by not storing any user credentials. It only validates credentials and returns the user's profile information.

# How to use pesu-auth

You can use the API to authenticate your PESU credentials using a simple ```POST``` request. Here is an example using Python:

```python
import requests

data = {
    'username': 'your_SRN_or_PRN',
    'password': 'your_password'
}

response = requests.post('https://pesu-auth.herokuapp.com/', data=data)
```

On authentication, it returns the following parameters in a JSON object. If the sign-in was successful, the response's 
`profile-data` key will store a dictionary with a user's profile information. On an unsuccessful sign-in, this field will hold an empty dictionary.

```json
{
    "authentication-status": , 
    "timestamp": , 
    "profile-data": 
        {
            "name": , 
            "prn": , 
            "srn": , 
            "degree": , 
            "branch": , 
            "semester": ,
            "section": 
        }
}
```