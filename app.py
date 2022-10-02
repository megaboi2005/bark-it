import json
from time import time
import cryptocode
from flask import (
    Flask, abort, redirect, render_template, request, send_file,
    send_from_directory, url_for)
from werkzeug.datastructures import ImmutableMultiDict
from flask import session
from random import randrange
global post

post = open("templates/post.html", "r").read()
app = Flask(__name__)
app.secret_key = b'secretkey'


def loadjson():
    return open("json/posts.json", "r").read()

def filter(var):
    '''Sanitizes user input'''
    return var.replace('\\', '&#92;'
        ).replace('\"', '&quot;'
        ).replace('\'', '&#39;'
        ).replace('<', '&lt;'
        ).replace('>', '&gt;').strip()


def genposts(page):
    output = ""
    print(len(json.loads(loadjson())))
    for a in range(3):
        print(a)
        pcount = len(json.loads(loadjson())) - a - int(page) 
        try:
            output += (
                post.replace(
                    "^user^", str(json.loads(loadjson())[f"{pcount}"]["author"])
                )
                .replace("^title^", str(json.loads(loadjson())[f"{pcount}"]["title"]))
                .replace(
                    "^content^", str(json.loads(loadjson())[f"{pcount}"]["content"])
                )
                .replace("{PostID}", str(pcount))
            )
        except KeyError:
            pass

    return output


def genpost(id):
    postload = json.loads(open("json/posts.json", "r").read())[id]
    return (
        post.replace("^user^", postload["author"])
        .replace("^title^", postload["title"])
        .replace("^content^", postload["content"])
        
        .replace("^right^",f"/posts/{id-1}")
        .replace("^left^",f"/posts/{id-1}")
    )


def getData(file):
    """Gets the json data from {file}"""
    return json.loads(open(file, "r").read())

def checkban(user):
    userread = json.loads(open("json/users.json","r").read())
    if userread[user]["banned"] == "True":
        return True
    else:
        return False
@app.route("/")
def main(name=None):
    global processing_time
    global posts
    start = time()
    posts = open("templates/genposts.html","r").read()
    resp = open("templates/index.html","r").read()
    end = time()
    processing_time = end - start
    try:
        name = session["name"]
    except:
        name = "Login"
    return (
        resp.replace("^render^", str(processing_time))
        .replace("^right^", "/posts/1")
        .replace("^left^", "/posts/1")
        .replace("^profile^",name)
        .replace("^posts^",posts)
    )


@app.route("/images/<path:filename>")
def images(filename):
    
    if filename == "bark-it.png":
        chance = randrange(1,1000)
        print(chance)
        if chance == 69:
            return send_from_directory("images", "meow-it.png", as_attachment=True) 
    if filename == "bark-it-small.png":
        chance = randrange(1,1000)
        if chance == 69:
            return send_from_directory("images", "meow-it-small.png", as_attachment=True) 
    try:
        return send_from_directory(
            "images", filename, as_attachment=True
        )

    except FileNotFoundError:
        abort(404)


@app.route("/about")
def about():
    try:
        sessname = session["name"]
    except:
        sessname = "Login"
    return open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^",open("templates/about.html").read()) 


# api
@app.route("/postget/<id>/")
def postget(id):

    try:
        return json.loads(loadjson())[id]

    except:
        return "null"

@app.route("/postcount")
def postcount():
    return str(len(json.loads(loadjson())))

#@app.route("/comments/<id>/")
#def comments(id):
#    return render_template("index.html", posts=genpost(id))


@app.route("/sendpost/", methods=["GET", "POST", "DELETE"])
def user():
    if request.method == "GET":
        try:
            sessname = session["name"]
            if checkban(sessname):
                return "you are banned"
        except:
            return open("templates/index.html","r").read().replace("^profile^","Login").replace("^posts^","not logged in") 
        title = request.args.get('title')
        content = request.args.get('post')

        if title == None:
            form = """
<div class=posts>
    <center>
    <form action="/sendpost">
        <label for="id1">Title </label>
        <br>
        <input class=input type="text" id="id1" name="title" required>
        <br>
        <label for="id2">Content  </label>
        <br>
        <textarea class=input style="resize: vertical;" rows=10 maxlength="6000" id="id2" name="post" required></textarea>
        <br>
        <input class=styledbutton style="width: 30%; height: 50%;" type="submit" value="Submit">
    </form>
    </center>
</div>"""   
            try:
                name = session["name"]
            except:
                name = "Login"
                return open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^","not logged in") 
            return open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^",form)
        if len(content) > 6000 or len(title) > 6000:
            return "post size is too big" 

        try:  
            token = "0"
            posts = getData("json/posts.json")
            newPostId = max(map(int, posts.keys())) + 1
            postfile = open("json/posts.json", "w")
            posts.update(
                {
                    newPostId: {
                        "title": title,
                        "author": sessname,
                        "content": content,
                        "likes": 1,
                        "locked": False,
                        "comments": {},
                    }
                }
            )
            postfile.write(json.dumps(posts, indent=2))
            print(f"Name: {sessname}, Title: '{title}'\nContent: {content}")
            return '<meta http-equiv="Refresh" content="0; url=/sendpost" />'
        except:
            return '<meta http-equiv="Refresh" content="0"; url=/sendpost" />'

    else:
        return f"{request.method} requests don't work on this url"
@app.route("/login/")
def login():

    form = """

    <div class=posts>
        <form action="/login">
            <label for="id1">Username </label>
            <input class=input type="text" id="id1" name="name">
            <br>
            <label for="id2">Password  </label>
            <input class=input type="password" id="id2" name="pass">
            <br>
            <input type="submit" value="Submit">
        </form>
    </div>"""
    userread = json.loads(open("json/users.json","r").read())
    name = request.args.get('name')
    password = request.args.get('pass')

    try:
        sessname = session["name"]
    except:
        sessname = "Login"

    if name == None or password == None:
        return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^",form)
    else:
        try:
            if checkban(name):
                return "you are banned"
            decrypt = cryptocode.decrypt(userread[name]["password"], password)
            #if decrypt == False:
                #return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^","<center><p>incorrect username or password</p></center> "+form)
            if decrypt == password:
                session['name'] = name
            else:
                return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^","<center><p>incorrect username or password</p></center> "+form)
            return '<meta http-equiv="Refresh" content="0; url=/" />'
        except:
            return '<meta http-equiv="Refresh" content="0; url=/" />'
    if not title or not content:
        return "notfinished"

@app.route("/register/")
def register():

    try:
        sessname = session["name"]
    except:
        sessname = "Login"
    form = """
    <div class=posts>
        <form action="/register">
            <label for="id1">Username </label>
            <input class=input type="text" id="id1" name="name">
            <br>
            <label for="id2">Password  </label>
            <input class=input type="password" id="id2" name="pass">
            <br>
            <input type="submit" value="Submit">
        </form>
    </div>"""
    
    userread = json.loads(open("json/users.json","r").read())
    name = request.args.get('name')
    password = request.args.get('pass')
    
    if name == None or password == None:
        return open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^",form)
    for item in userread:
        if name == item:
           
            return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^","<p>Name already taken</p> "+form)
    password = cryptocode.encrypt(password,password)
    userwrite = open("json/users.json","w")
    userread.update({name : {"password" : password, "banned" : "False"}})
    userwrite.write(json.dumps(userread, indent=2))

    return open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^",form)

@app.route("/settings/")
def settings():
    try:
        sessname = session["name"]
    except:
        sessname = "Login"
    if sessname == "admin":
        return open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^",open("templates/settingsadmin.html","r").read())
    return open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^",open("templates/settings.html","r").read())

@app.route("/chngsetting/<setting>")
def chngsettings(setting):
    try:
        sessname = session["name"]
    except:
        return "please log in"
    match setting:
        case "changepass":
            password = request.args.get('oldpass')
            newpass = request.args.get('newpass')
            newpass2 = request.args.get('newpass2')
            if not newpass == newpass2:
                 return '<meta http-equiv="Refresh" content="2; url=/settings"/><p>new passwords do not match</p>'
            userread = json.loads(open("json/users.json","r").read())
            if not len(newpass) >= 1:
                return "put in a new password"

            if cryptocode.decrypt(userread[sessname]["password"],password) == password:
                userread[sessname]["password"] = cryptocode.encrypt(newpass,newpass)
                usersave = open("json/users.json","w").write(json.dumps(userread, indent=2))
                return '<meta http-equiv="Refresh" content="0; url=/" />'
            else:
                return "wrong password"


        case "adminban":
            if not sessname == "admin":
                return "you are not an admin"
            try:
                user = request.args.get('user')
            except:
                return "no user"
            userread = json.loads(open("json/users.json","r").read())
            try:
                userread[user]["banned"] = "True"
            except KeyError:
                return "unknown user"
            usersave = open("json/users.json","w").write(json.dumps(userread, indent=2))
            return "banned"

        case "adminunban":
            if not sessname == "admin":
                return "you are not an admin"
            try:
                user = request.args.get('user')
            except:
                return "no user"
            userread = json.loads(open("json/users.json","r").read())
            userread[user]["banned"] = "False"
            usersave = open("json/users.json","w").write(json.dumps(userread, indent=2))
            return "unbanned"

if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
