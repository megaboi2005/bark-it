import json
from aiohttp import web
from os.path import exists
from cryptography.fernet import Fernet

def getPost(id):
    '''Gets the post that has the post id'''
    return(json.load(open("json/posts.json"))[str(id)])

def cutList(theList, n):
    '''Cuts a list into chunks of n size'''
    return [theList[i * n:(i + 1) * n] for i in range((len(theList) + n - 1) // n)]

def form(name, desc, location):
	form = open('elements/form.html','r')
	formout = form.read()
	return formout.replace('{name}', name).replace('{location}', location).replace('{desc}', desc)

def getData(file):
    '''Gets the json data from {file}'''
    return json.loads(open(file, 'r').read())

def filter(var):
    '''Sanitizes user input'''
    return var.replace('\\', '&#92;'
        ).replace('\"', '&quot;'
        ).replace('\'', '&#39;'
        ).replace('<', '&lt;'
        ).replace('>', '&gt;').strip()

def getUsername(request): 
    return request.rel_url.query['name']

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
            return web.Response(text='account exists', content_type='text/html')

        # Adds the user
        else:
            userwrite = open('json/users.json','w')
            userwrite.write(json.dumps(data, indent=2))
            print('The user"'+name+'" was added.')
            return web.Response(text='yay', content_type='text/html')

        return web.Response(text='something went wrong sorry', content_type='text/html')

    except KeyError:
        formin = form('name','pass','register')
        return web.Response(text=formin, content_type='text/html')

async def post(request):
    indexFile = open('index.html','r').read()
    try:
        name = filter(getUsername(request))
        content = filter(request.rel_url.query['post'])
        title = filter(request.rel_url.query['title'])

        if name == '' or post == '' or title == '':
            return web.Response(text=indexFile.replace('^posts^', 'You can\'t do that.'), content_type='text/html')
        
        posts = getData("json/posts.json")
        newPostId = max(map(int, posts.keys()))+1
        postfile = open('json/posts.json', 'w')
        posts.update({newPostId:{"title":title, "author":name, "content":content, "likes":1, "locked":False, "comments":{}}})
        postfile.write(json.dumps(posts, indent=2))
        print(f"Name: '{name}', Title: '{title}'\nContent: {content}")
        return web.Response(text='<meta http-equiv="Refresh" content="0; url=/" />',content_type='text/html')

    except:
        output = indexFile.replace('^posts^', '''
<div class=post>
  <form action="/post">
    <label for="id">Title: </label><input type="text" id="title" name="title"><br>
    <label for="id">Username: </label><input type="text" id="name" name="name"><br>
    <label for="id">Content: </label><br>
    <textarea id="post" name="post" rows="4" cols="50"></textarea>
    </p><br><input type="submit" value="Submit">
  </form>
</div>''')
        return web.Response(text=output, content_type='text/html')

async def main(request):
    try:
        page = int(request.rel_url.query['page'])
    except:
        page = 0

    posts = ""
    numPosts = cutList(list(json.load(open("json/posts.json", "r")).keys())[::-1], 3)
    try:
        postsForPage = numPosts[page]
    except:
        postsForPage = numPosts[0]

    for id in postsForPage:
        currentPost = getPost(id)
        posts += f"""<div class=post>
  <p class=name rows="2" readonly>
    "<b>{currentPost["title"]}</b>" {"&#x1F512;" if currentPost["locked"] else ""}
    <br> posted by <b>{currentPost["author"]}</b>
  </p>
  <p class=textpost>
    {currentPost["content"]}
  </p>
  <br>
    {"<a href=/comments?id={id}><button>comments (don't work yet)</button></a>" if not currentPost["locked"] else ""}
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
    web.get('/post', post),
    web.static('/images', "elements", show_index=True)
])
web.run_app(app)

