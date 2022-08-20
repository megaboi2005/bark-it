import json
from time import time

from flask import (
    Flask, abort, redirect, render_template, request, send_file,
    send_from_directory, url_for)
from werkzeug.datastructures import ImmutableMultiDict
from flask import session
global post

post = open("templates/post.html", "r").read()
app = Flask(__name__)
app.secret_key = b'aodhukasdhuiladhiouladhuioadhukladhkuashduklahi8'

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





def getData(file):
    """Gets the json data from {file}"""
    return json.loads(open(file, "r").read())


@app.route("/")
def main(name=None):
    global processing_time
    global posts
    start = time()
    posts = genposts(0)
    resp = render_template("index.html", posts=posts)
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
    )


@app.route("/images/<path:filename>")
def images(filename):
    try:
        return send_from_directory(
            "images", filename, as_attachment=True
        )

    except FileNotFoundError:
        abort(404)


@app.route("/posts/<page>/")
def posts(page):
    start = time()
    posts = genposts(page)
    resp = render_template("index.html", posts=posts)
    end = time()
    processing_time = end - start
    try:
        name = session["name"]
    except:
        name = "Login"
    return (
        resp.replace("^render^", str(processing_time))
        .replace("^right^", f"/posts/{str(int(page) + 1)}")
        .replace("^left^", f"/posts/{str(int(page) - 1)}")
        .replace("^profile^", name)
    )


# api
@app.route("/postget/<id>/")
def postget(id):

    try:
        return loadjson()[id]

    except KeyError:
        return "unknown post"


@app.route("/comments/<id>/")
def comments(id):
    post = loadjson()[id]
    return render_template("index.html", posts="lol no comments yet")


@app.route("/sendpost/", methods=["GET", "POST", "DELETE"])
def user():
    if request.method == "GET":
        try:
            sessname = session["name"]
        except:
            return open("templates/index.html","r").read().replace("^profile^","Login").replace("{{ posts|safe }}","not logged in") 
        title = request.args.get('title')
        content = request.args.get('post')

        if title == None:
            form = """
<div class=post>
    <form action="/sendpost">
        <label for="id1">Title </label>
        <input type="text" id="id1" name="title">
        <br>
        <label for="id2">Content  </label>
        <textarea id="post" name="post" rows="4" cols="50"></textarea>
        <br>
        <input type="submit" value="Submit">
    </form>
</div>"""   
            try:
                name = session["name"]
            except:
                name = "Login"
                return open("templates/index.html","r").read().replace("^profile^",sessname).replace("{{ posts|safe }}","not logged in") 
            return open("templates/index.html","r").read().replace("^profile^",sessname).replace("{{ posts|safe }}",form) 
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
            return '<meta http-equiv="Refresh" content="0; url=/" />'
        except:
            return '<meta http-equiv="Refresh" content="0"; url=/" />'

    else:
        return f"{request.method} requests don't work on this url"
@app.route("/login/")
def login():
    form = """
    <div class=post>
        <form action="/login">
            <label for="id1">Username </label>
            <input type="text" id="id1" name="name">
            <br>
            <label for="id2">Password  </label>
            <input type="password" id="id2" name="pass">
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
        return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("{{ posts|safe }}",form)
    else:
        try:
            if userread[name]["password"] == password:
                session['name'] = name
            else:
                return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("{{ posts|safe }}","<p>incorrect username or password</p> "+form)
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
    <div class=post>
        <form action="/register">
            <label for="id1">Username </label>
            <input type="text" id="id1" name="name">
            <br>
            <label for="id2">Password  </label>
            <input type="password" id="id2" name="pass">
            <br>
            <input type="submit" value="Submit">
        </form>
    </div>"""
    
    userread = json.loads(open("json/users.json","r").read())
    name = request.args.get('name')
    password = request.args.get('pass')
    if name == None or password == None:
        return open("templates/index.html","r").read().replace("^profile^",sessname).replace("{{ posts|safe }}",form)
    for item in userread:
        if name == item:
           
            return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("{{ posts|safe }}","<p>Name already taken</p> "+form)
    
    userwrite = open("json/users.json","w")
    userread.update({name : {"password" : password}})
    userwrite.write(json.dumps(userread, indent=2))

    return '<meta http-equiv="Refresh" content="0; url=/" />'


@app.route("/about")
def aboutpage():
    about = open("templates/about.html","r").read()
    try:
        name = session["name"]
    except:
        name = "Login"
    return  open("templates/index.html","r").read().replace("^profile^",name).replace("{{ posts|safe }}",about)

if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
