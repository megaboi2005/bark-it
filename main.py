import json
from aiohttp import web
from os.path import exists
from cryptography.fernet import Fernet

def getPost(id):
    return(json.load(open("json/posts.json"))[str(id)])

def form(name,desc,location):
	form = open('elements/form.html','r')
	formout = form.read()
	return formout.replace('{name}',name).replace('{location}',location).replace('{desc}',desc)

def getData(file):
    '''Gets the json data from {file}'''
    return json.loads(open(file, 'r+').read())

def filter(var):
    '''Sanitizes user input'''
    return var.replace('\\', '\\\\'
        ).replace('\"', '\\\"'
        ).replace('\'', '\\\''
        ).replace('<', '&lt'
        ).replace('>', '&gt;')

async def register(request):
    try:
        # Gets the name and password.
        name = request.rel_url.query['name']
        password = request.rel_url.query['pass']
        finalname = filter(name)
        finalpass = str(f.encrypt(filter(password).encode()))
        # Gets a list of existing users
        users = getData('json/users.json').keys()
        # Get current data and updates it
        data = getData('json/users.json')
        data.update({finalname:{'password':finalpass, 'posts':[]}})
        # Stops users from making an account that already exists
        if name in users:
            return web.Response(text='account exists',content_type='text/html')

        # Adds the user
        else:
            userwrite = open('json/users.json','w')
            userwrite.write(json.dumps(data, indent=2))
            print('The user"'+name+'" was added.')
            return web.Response(text='yay',content_type='text/html')

        return web.Response(text='something went wrong sorry',content_type='text/html')

    except KeyError:
        formin = form('name','pass','register')
        return web.Response(text=formin,content_type='text/html')

async def main(request):
    posts = ""
    for id in range(len(json.load(open("json/posts.json", "r")).keys())):
        currentPost = getPost(id)
        posts += f"""<div class=post>
  <p class=name rows="2" readonly>
    "<b>{currentPost["title"]}</b>" {"&#x1F512;" if currentPost["locked"] else ""}
    <br> posted by <b>{currentPost["author"]}</b>
  </p>
  <textarea readonly class=textpost>
    {currentPost["content"]}
  </textarea>
  <br>
    <a href=/comments?id={id}>
      <button>comments (don't work yet)</button>
    </a>
  </br>
</div>"""
    page = open("index.html").read().replace("^posts^", posts)
    return web.Response(text=page, content_type='text/html')

# Generates the key if it doesn't exist
if not exists('secret.key'):
    key = Fernet.generate_key()
    key_file = open('secret.key', 'wb')
    key_file.write(key)

key = open('secret.key', 'rb').read()
f = Fernet(key)

# Starts the web app
app = web.Application()
app.add_routes([
    web.get('/register', register),
    web.get('/index', main),
    web.get('/', main),
    web.static('/images', "elements", show_index=True)
])
web.run_app(app)

