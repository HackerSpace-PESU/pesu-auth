# pesu-auth
A simple API to authenticate PESU credentials using PESU Academy

# How to use pesu-auth

You can use the API to authenticate your PESU credentials using a simple POST request. Here is an example using Python:

```python
import requests

data = {
    'username': 'your_SRN_or_PRN',
    'password': 'your_password'
}

response = requests.post('https://pesu-auth.herokuapp.com/', data=data)

```