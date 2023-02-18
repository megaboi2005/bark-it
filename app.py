import json
from time import time
import cryptocode
from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from werkzeug.datastructures import ImmutableMultiDict
from flask import session
from random import randrange
from Levenshtein import distance

global post

post = open("templates/post.html", "r").read()
app = Flask(__name__)
app.secret_key = b"secretkey"


def loadjson():
    return open("json/posts.json", "r").read()


def filter(var):
    """Sanitizes user input"""
    return (
        var.replace("\\", "&#92;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .strip()
    )


def genposts(page):
    output = ""
    posts = loadjson()
    for a in range(3):
        pcount = len(posts) - a - int(page)
        if posts.get(f"{pcount}") == None:
            continue
        output += (
            post.replace(
                "^user^", str(posts[f"{pcount}"].get("author", "Unknown User"))
            )
            .replace("^title^", str(posts[f"{pcount}"].get("title", "Unknown Title")))
            .replace(
                "^content^", str(posts[f"{pcount}"].get("content", ""))
            )
            .replace("{PostID}", str(pcount))
        )

    return output


def genpost(id):
    postload = json.loads(open("json/posts.json", "r").read()).get(id, {})
    return (
        post.replace("^user^", postload.get("author", "Unknown User"))
        .replace("^title^", postload.get("title", "Unknown Title"))
        .replace("^content^", postload.get("content", ""))
        .replace("^right^", f"/posts/{id-1}")
        .replace("^left^", f"/posts/{id-1}")
    )


def getData(file):
    """Gets the json data from {file}"""
    return json.loads(open(file, "r").read())


def checkban(user):
    userread = json.loads(open("json/users.json", "r").read())
    if userread[user].get("banned") == "True":
        return True
    else:
        return False


@app.route("/")
def main(name=None):
    global processing_time
    global posts
    start = time()
    posts = open("templates/genposts.html", "r").read()
    resp = open("templates/index.html", "r").read()
    end = time()
    processing_time = end - start
    name = session.get("name", "Login")
    return (
        resp.replace("^render^", str(processing_time))
        .replace("^right^", "/posts/1")
        .replace("^left^", "/posts/1")
        .replace("^profile^", name)
        .replace("^posts^", posts)
        .replace("^title^", "Main")
    )


@app.route("/images/<path:filename>")
def images(filename):

    if filename == "bark-it.png":
        chance = randrange(1, 1000)
        print(chance)
        if chance == 69:
            return send_from_directory("images", "meow-it.png", as_attachment=True)
    if filename == "bark-it-small.png":
        chance = randrange(1, 1000)
        if chance == 69:
            return send_from_directory(
                "images", "meow-it-small.png", as_attachment=True
            )
    try:
        return send_from_directory("images", filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route("/about")
def about():
    sessname = session.get("name", "Login")
    return (
        open("templates/index.html", "r")
        .read()
        .replace("^profile^", sessname)
        .replace("^posts^", open("templates/about.html").read())
        .replace("^title^", "About")
    )


# API
@app.route("/postget/<id>/")
def postget(id):
    return json.loads(loadjson()).get(id, "nill")


@app.route("/postcount")
def postcount():
    return str(len(json.loads(loadjson())))


# @app.route("/comments/<id>/")
# def comments(id):
#    return render_template("index.html", posts=genpost(id))


@app.route("/sendpost/", methods=["GET", "POST", "DELETE"])
def user():
    if request.method == "GET":
        sessname = session.get("name")
        if sessname:
            if checkban(sessname):
                return "you are banned"
        else:
            return (
                open("templates/index.html", "r")
                .read()
                .replace("^profile^", "Login")
                .replace("^posts^", "not logged in")
                .replace("^title^", "Sending posts")
            )
        title = request.args.get("title")
        content = request.args.get("post")

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
            name = session["name"]
            if name == None:
                name = "Login"
                return (
                    open("templates/index.html", "r")
                    .read()
                    .replace("^profile^", sessname)
                    .replace("^posts^", "not logged in")
                    .replace("^title^", "Login")
                )
            return (
                open("templates/index.html", "r")
                .read()
                .replace("^profile^", sessname)
                .replace("^posts^", form)
                .replace("^title^", sessname)

            )
        if len(content) > 6000 or len(title) > 6000:
            return "post size is too big"

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
    userread = json.loads(open("json/users.json", "r").read())
    name = request.args.get("name")
    password = request.args.get("pass")
    
    sessname = session.get("name", "Login")
    
        

    if name == None or password == None:
        return (
            open("templates/index.html", "r")
            .read()
            .replace("^profile^", sessname)
            .replace("^posts^", form)
            .replace("^title^", "Login")
        )
    else:
        if checkban(name):
            return "you are banned"
        decrypt = cryptocode.decrypt(userread[name]["password"], password)
        # if decrypt == False:
        # return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^","<center><p>incorrect username or password</p></center> "+form)
        if decrypt == password:
            session["name"] = name
        else:
            return (
                open("templates/index.html", "r")
                .read()
                .replace("^profile^", sessname)
                .replace(
                    "^posts^",
                    "<center><p>incorrect username or password</p></center> "
                    + form,
                )
                .replace("^title^", "Login")
            )
        return '<meta http-equiv="Refresh" content="0; url=/" />'
    


@app.route("/register/")
def register():

    sessname = session.get("name", "Login")
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

    userread = json.loads(open("json/users.json", "r").read())
    name = request.args.get("name")
    password = request.args.get("pass")

    if name == None or password == None:
        return (
            open("templates/index.html", "r")
            .read()
            .replace("^profile^", sessname)
            .replace("^posts^", form)
            .replace("^title^", "Register")
        )
    for item in userread:
        if name == item:
            return (
                open("templates/index.html", "r")
                .read()
                .replace("^profile^", sessname)
                .replace("^posts^", "<p>Name already taken</p> " + form)
                .replace("^title^", "Register")
            )
    password = cryptocode.encrypt(password, password)
    userwrite = open("json/users.json", "w")
    userread.update({name: {"password": password, "banned": "False"}})
    userwrite.write(json.dumps(userread, indent=2))

    return (
        open("templates/index.html", "r")
        .read()
        .replace("^profile^", sessname)
        .replace("^posts^", form)
        .replace("^title^", "Register")
    )


@app.route("/settings/")
def settings():
    sessname = session.get("name", "Login")
    if sessname == "admin":
        return (
            open("templates/index.html", "r")
            .read()
            .replace("^profile^", sessname)
            .replace("^posts^", open("templates/settingsadmin.html", "r").read())
            .replace("^title^", "Settings")
        )
    return (
        open("templates/index.html", "r")
        .read()
        .replace("^profile^", sessname)
        .replace("^posts^", open("templates/settings.html", "r").read())
        .replace("^title^", "Settings")
    )


@app.route("/chngsetting/<setting>")
def chngsettings(setting):
    sessname = session.get("name", "Please log in")
    match setting:
        case "changepass":
            password = request.args.get("oldpass")
            newpass = request.args.get("newpass")
            newpass2 = request.args.get("newpass2")
            if not newpass == newpass2:
                return '<meta http-equiv="Refresh" content="2; url=/settings"/><p>new passwords do not match</p>'
            userread = json.loads(open("json/users.json", "r").read())
            if not len(newpass) >= 1:
                return "put in a new password"

            if cryptocode.decrypt(userread[sessname]["password"], password) == password:
                userread[sessname]["password"] = cryptocode.encrypt(newpass, newpass)
                usersave = open("json/users.json", "w").write(
                    json.dumps(userread, indent=2)
                )
                return '<meta http-equiv="Refresh" content="0; url=/" />'
            else:
                return "wrong password"

        case "adminban":
            if not sessname == "admin":
                return "you are not an admin"
            user = request.args.get("user", "no user")
            userread = json.loads(open("json/users.json", "r").read())
            if userread.get(user):
                userread[user]["banned"] = "True"
            else:
                return "unknown user"
            usersave = open("json/users.json", "w").write(
                json.dumps(userread, indent=2)
            )
            return "banned"

        case "adminunban":
            if not sessname == "admin":
                return "you are not an admin"
            user = request.args.get("user", "no user")
            userread = json.loads(open("json/users.json", "r").read())
            userread[user]["banned"] = "False"
            usersave = open("json/users.json", "w").write(
                json.dumps(userread, indent=2)
            )
            return "unbanned"
@app.route("/search/")
def searchpage():
    sessname = session.get("name", "Login")
    object = request.args.get("object")
    searched = request.args.get("search")
    index = open("templates/index.html", "r").read()

    if searched and object:
        if object == "channel":
            channels = json.load(open("json/catagories.json", "r"))
            channellist = [c["name"] for c in channels.values() if distance(searched, c["name"]) < 4]
            return channellist

        elif object == "posts":
            posts = json.load(open("json/posts.json", "r"))
            post_template = open("templates/post.html", "r").read()
            postslist = [p for p in posts.values() if distance(searched, p["title"]) < 4]
            postsrender = "".join([post_template.replace("^user^", p["author"]).replace("^title^", p["title"]).replace("^content^", p["content"]) for p in postslist])
            return index.replace("^posts^", postsrender).replace("^profile^", sessname)

    return index.replace("^profile^", sessname).replace("^posts^", open("templates/search.html", "r").read().replace("^title^", "Search"))
    
@app.route("/channels")
def channels():
    sessname = session.get("name", "Login")
    return (
        open("templates/index.html", "r")
        .read()
        .replace("^profile^", sessname)
        .replace("^posts^", open("templates/channels.html").read())
        .replace("^title^", "Channels")
    )

@app.route("/report")
def report():
    sessname = session.get("name", "Login")
    return (
        open("templates/index.html", "r")
        .read()
        .replace("^profile^", sessname)
        .replace("^posts^", open("templates/report.html").read())
        .replace("^title^", "Report")
    )

if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
