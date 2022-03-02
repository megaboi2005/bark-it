import json
import base64
from aiohttp import web
from os.path import exists
from cryptography.fernet import Fernet
from pprint import pformat
from datetime import datetime
import random
from random import randrange
response = web.HTTPSeeOther('/')
indexFile = open('index.html','r').read()
now = datetime.now()
def getPost(id):
    '''Gets the post that has the post id'''
    return(json.load(open("json/posts.json"))[str(id)])

def cutList(theList, n):
    '''Cuts a list into chunks of n size'''
    return [theList[i * n:(i + 1) * n] for i in range((len(theList) + n - 1) // n)]

def form(name, desc, location):
	form = open('elements/login.html','r')
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

#pls help me find a different way
def readcookie(request,name):
    output = pformat(request)[13:-1].replace("'",'"')
    loaded = json.loads(output)
    return loaded[name]

def loadindex(posts,request):
    jsonfile = getData('json/users.json')
    
    output = pformat(request.cookies)[13:-1].replace("'",'"')
    loaded = json.loads(output)
    try:
        for a in jsonfile:
            
            if str(jsonfile[a]["token"]) in loaded["auth"]:
                output = a
                break
    except KeyError:
        a = 'login'
    output = f'<a href=/login><button>{a}</button></a>'
    return indexFile.replace('^posts^',posts).replace('^profile^',output)

def getname(request):

    jsonfile = getData('json/users.json')
    
    output = pformat(request.cookies)[13:-1].replace("'",'"')
    loaded = json.loads(output)
    for a in jsonfile:
        if str(jsonfile[a]["token"]) == loaded["auth"]:
            output = a
            break
    return a
async def register(request):
    
    try:
        
        # Gets the name and password.
        name = request.rel_url.query['name']
        password = request.rel_url.query['pass']
        finalname = filter(name)
        #finalpass = str(f.encrypt(filter(password).encode()))
        # Gets a list of existing users
        users = getData('json/users.json')
        # Get current data and updates it
        month = datetime.now().month
        d = datetime.now().day
        h = now.strftime("%H")
        m = now.strftime("%M")
        s = now.strftime("%S")
        jsonfile = getData('json/users.json')
        
        output = False
        while output == False:
            token = randrange(1,100000000000000000000)
            for a in jsonfile:
                if jsonfile[a]["token"] == token:
                    output = False
                    break
                output = True
        


        data = getData('json/users.json')
        data.update({finalname:{'password':password, 'posts':[], 'token':token}})
        # Stops users from making an account that already exists
        if name in users:
            formin = form('name','pass','register')
            output = f'</p>Sorry this account is taken</p>{formin}'
            return web.Response(text=indexFile.replace('^posts^',output), content_type='text/html')
        
        special_characters = "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
        password_numbers = "1234567890"
        
        if not any(x in special_characters for x in password) or len(password) <= 5 or not any(y in password_numbers for y in password):
            formin = form('name','pass','register')
            output = f'</p>Your password needs special characters, numbers, and be longer than 5 characters</p>{formin}'
            return web.Response(text=indexFile.replace('^posts^',output), content_type='text/html')
        
        # Adds the user
        else:
            userwrite = open('json/users.json','w')
            userwrite.write(json.dumps(data, indent=2))
            print('The user"'+name+'" was added.')
            
            return web.Response(text=indexFile.replace('^posts^','Account created'), content_type='text/html')

        return web.Response(text='something went wrong sorry', content_type='text/html')

    except KeyError:
        formin = form('name','pass','register')
        
        return web.Response(text=indexFile.replace('^posts',formin), content_type='text/html')

async def post(request):
    indexFile = open('index.html','r').read()
    try:
        name = getname(request)

        content = filter(request.rel_url.query['post'])
        title = filter(request.rel_url.query['title'])
        

        banned_word = ['eWVz']
        splitPost = post.split(' ');
        splitTitle = title.split(' ');
        
        def checkBanned(postVariable):
            for x in banned_word:
                if x in postVariable:
                    return web.Response(text=indexFile.replace('^posts^', 'A word in your post is banned for NSFW.'), content_type = 'text/html');
        
        for j in splitPost:
            j_bytes = j.encode('ascii')
            base64_bytes = base64.b64encode(j_bytes)
            j_base64 = base64_bytes.decode('ascii')
            
            checkBanned(j_base64);
            
                    
        for t in splitTitle:
            t_bytes = t.encode('ascii')
            tbase64_bytes = tbase64.b64encode(t_bytes)
            t_base64 = tbase64_bytes.decode('ascii')
            
            checkBanned(t_base64);

        
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
   
    
    return web.Response(text=loadindex(posts,request).replace('^left^',f'/?page={page-1}').replace('^right^',f'/?page={page+1}'), content_type='text/html')

async def login(request):
    try:
        name = request.rel_url.query['name']
        password = request.rel_url.query['pass']
        
        users = getData('json/users.json')
        readusers = users[name]["token"]
        userpass = users[name]["password"]
        if not password == userpass:
            formin = form('name','pass','login')
            return web.Response(text=indexFile.replace('^posts',f'<p>incorrect password</p>{formin}'), content_type='text/html')
        response.cookies['auth'] = readusers
        return response
    except KeyError:
        formin = form('name','pass','login')
        return web.Response(text=indexFile.replace('^posts',formin), content_type='text/html')
   
async def about(request):
    about = open('elements/about.html','r').read()
    
    return web.Response(text=loadindex(about,request), content_type='text/html')
    
    
# Generates the key if it doesn't exist
#if not exists('secret.key'):
#    key = Fernet.generate_key()
#    key_file = open('secret.key', 'wb')
#    key_file.write(key)
#    key_file.close()

#key = open('secret.key', 'rb').read()
#f = Fernet(key)

# Starts the web app
app = web.Application()
app.add_routes([
    web.get('/register', register),
    web.get('/index', main),
    web.get('/', main),
    web.get('/post', post),
    web.get('/login', login),
    web.get('/about', about),
    web.static('/images', "elements", show_index=True)
])
web.run_app(app)

