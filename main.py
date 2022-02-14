import json
from aiohttp import web
from os.path import exists
from cryptography.fernet import Fernet

def getData(file):
    '''Gets the json data from {file}'''
    return json.loads(open(file, "r+").read())

def filter(var):
    '''Sanitizes user input'''
    return var.replace("\\", "\\\\"
        ).replace('"','\"'
        ).replace('<',' &lt'
        ).replace('>','&gt;'
        ).replace("'",'\'')

async def register(request):
    try:
        # Gets the name and password.
        name = request.rel_url.query['name']
        password = request.rel_url.query['pass']
        finalname = filter(name)
        finalpass = str(f.encrypt(filter(password).encode()))
        # Gets a list of existing users
        users = getData('users/users.json').keys()
        # Get current data and updates it
        data = getData('users/users.json')
        data.update({finalname:{"password":finalpass, "posts":[]}})
        # Stops users from making an account that already exists
        if name in users:
            return web.Response(text='account exists',content_type='text/html')
        # Adds the user
        else:
            userwrite = open('users/users.json','w')
            userwrite.write(json.dumps(data, indent=2))
            return web.Response(text='yay',content_type='text/html')
        return web.Response(text='something went wrong sorry',content_type='text/html')

    except KeyError:
        formin = getData('users/users.json')
        return web.Response(text=formin,content_type='text/html')

# Generates the key if it doesn't exist
if not exists('secret.key'):
    key = Fernet.generate_key()
    key_file = open("secret.key", "wb")
    key_file.write(key)

key = open("secret.key", "rb").read()
f = Fernet(key)

# Starts the web app
app = web.Application()
app.add_routes([
                web.get('/register', register),
    ])
web.run_app(app)
