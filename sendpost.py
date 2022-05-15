import requests

url = 'http://localhost:5000/sendpost/'
myobj = {"title": "test","token": "xd","content": "Hello world"}

x = requests.post(url, data = myobj)

print(x.text)
