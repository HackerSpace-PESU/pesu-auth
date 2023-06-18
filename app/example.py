import requests

data = {
    'username': 'your SRN or PRN here',
    'password': 'your password here',
    'profile': False  # Optional, defaults to False
    # Set to True if you want to retrieve the user's profile information
}

response = requests.post("http://localhost:5000/authenticate", json=data)
print(response.json())
