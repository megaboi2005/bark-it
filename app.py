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
from werkzeug.utils import secure_filename
import os
from urllib.parse import urlparse
global post

post = open("templates/post.html", "r").read()
app = Flask(__name__,static_url_path='/files',static_folder='static')
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

def renderindex(page,title,session):
    index = open("templates/index.html","r").read()
    users = json.loads(open("json/users.json","r").read())
    try:
        userpfp = "/imagedatabase/"+users[session["name"]]["pfp"]+".png"
    except:
        userpfp = "/images/bark-it-small.png"
    user = session.get("name", "Login")
    return index.replace("^posts^",page).replace("^profile^",user).replace("^title^","Bark-IT - "+title).replace("^pfp^",userpfp)


def getuserprofile(user):
    users = json.loads(open("json/users.json","r").read())
    return "/imagedatabase/"+users[user]["pfp"]+".png"

@app.route("/")
def main(name=None):
    global processing_time
    global posts
    start = time()
    posts = open("templates/genposts.html", "r").read().replace("^api^","postget").replace("^counter^","postcount")
    end = time()
    processing_time = end - start
    user_agent = request.headers.get('User-Agent')
    print(user_agent.split('(')[1].split(')')[0])
    return renderindex(posts,"Home",session)

@app.route("/user/<name>")
def userpage(name):
    if name == None:
        return "invalid user"
    posts = open("templates/genposts.html", "r").read().replace("^api^","userget/"+name).replace("^counter^","/postcountuser/"+str(name))
    return renderindex(posts,name,session) + open("templates/profile.html", "r").read().replace("^pfp^",getuserprofile(name)).replace("^profile^",name)

@app.route("/userget/<user>/<id>")
def userget(user,id):
    try:
        return json.loads(loadjson())[getData("json/users.json")[user]["posts"][id]["id"]]
    except KeyError:
        return "null"

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


@app.route("/info")
def info():
    return renderindex(open("templates/about.html").read(),"About",session)

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
    
    if name == None or password == None:
        return renderindex(form,"Login",session)
    else:
        if checkban(name):
            return "you are banned"
        decrypt = cryptocode.decrypt(userread[name]["password"], password)
        # if decrypt == False:
        # return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^","<center><p>incorrect username or password</p></center> "+form)
        if decrypt == password:
            session["name"] = name
        else:
            return renderindex("<center><p>incorrect username or password</p></center> "+ form,"Login",session)
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
        return renderindex(form,"Register",session)
    for item in userread:
        if name == item:
            return renderindex("<p>Name already taken</p> ","Register",session)
    password = cryptocode.encrypt(password, password)
    userwrite = open("json/users.json", "w")
    
    userread.update(
        {
            name.replace(" ","_"): {
                "password": password, 
                "banned": "False",
                "posts": {},
                "pfp": "0"
                }
            
        }
    
    )

    userwrite.write(json.dumps(userread,indent=2))
    return '<meta http-equiv="Refresh" content="2; url=/login"/>'


@app.route("/settings/")
def settings():
    sessname = session.get("name", "Login")
    if sessname == "admin":
        return renderindex(open("templates/settingsadmin.html", "r").read(),"Admin Settings",session)
    return renderindex(open("templates/settings.html", "r").read(),"Settings",session)

    


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
    if not searched == None and not object == None:
        match object:
            case "channel":
                channellist = []
                channels = json.loads(open("json/catagories.json", "r").read())
                for i in range(len(channels)):
                    if distance(searched, channels[str(i)]["name"]) < 4:
                        channellist.append(channels[str(i)]["name"])
                return channellist
            case "posts":
                postslist = []
                postsrender = ""
                postspage = open("templates/post.html","r").read()
                posts = json.loads(open("json/posts.json", "r").read())
                for i in range(len(posts)):
                    if distance(searched, posts[str(i)]["title"]) < 4 or searched in posts[str(i)]["title"]:
                        postslist.append(posts[str(i)])
                        postsrender += postspage.replace("^user^",posts[str(i)]["author"]).replace("^title^",posts[str(i)]["title"]).replace("^content^",posts[str(i)]["content"]) + "<br>"
                return renderindex(postsrender,searched,session)
    else:
        return renderindex(open("templates/search.html", "r").read(),"Search",session)


# API
@app.route("/postget/<id>/")
def postget(id):
    return json.loads(loadjson()).get(id, "nill")


@app.route("/postcount")
def postcount():
    return str(len(json.loads(loadjson())))

@app.route("/postcountuser/<user>")
def postcountuser(user):
    return str(len(getData("json/users.json")[user]["posts"]))

@app.route("/imagedatabase/<path:filename>")
def profiledatabase(filename):
    try:
        return send_from_directory("imagedatabase", filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/uploadprofile', methods=['POST'])
def uploadpfp():
    
    if session.get("name","nope") == "nope":
        return '<meta http-equiv="Refresh" content="0; url=/"/>'
    f = request.files['file']
    userread = getData("json/users.json")
    
    extension = f.filename.split(".")[len(f.filename.split("."))-1]
    if not extension == "png":
        return "extension must be a png"
    if  userread[session["name"]]["pfp"] == "0":
        userwrite = open("json/users.json","w")
        f.save(os.path.join("imagedatabase", str(len(os.listdir("imagedatabase")))+"."+extension))
        userread[session["name"]]["pfp"] = str(len(os.listdir("imagedatabase"))-1)
        userwrite.write(json.dumps(userread,indent=2))
    else:
        f.save(os.path.join("imagedatabase", userread[session["name"]]["pfp"]+"."+extension))
    return '<meta http-equiv="Refresh" content="0; url=/"/>'


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
            return renderindex("not logged in","Post",session)

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
        <label for="id3">Channels (commas to seperate)</label>
        <input class=input type="text" id=id3 name="tags" required>
        <br>
        <input class=styledbutton style="width: 30%; height: 50%;" type="submit" value="Submit">
    </form>
    </center>
</div>"""
            name = session["name"]
            if name == None:
                name = "Login"
                return renderindex("not logged in","Post",session)
            return renderindex(form,"Post",session)          
        if len(content) > 6000 or len(title) > 6000:
            return "post size is too big"

        #token = "0"
        posts = getData("json/posts.json")
        users = getData("json/users.json")
        newPostId = max(map(int, posts.keys())) + 1
        postfile = open("json/posts.json", "w")
        usersfile = open("json/users.json","w")
        posts.update(
            {
                newPostId: {
                    "title": title,
                    "author": sessname,
                    "content": content.replace("<","&lt;").replace(">","&gt;"),
                    "likes": 1,
                    "locked": False,
                    "comments": {},
                }
            }
        )
        length = len(users[session["name"]]["posts"])
        users[session["name"]]["posts"].update(
            {length: {"id":str(newPostId)}}
        )
        postfile.write(json.dumps(posts, indent=2))
        usersfile.write(json.dumps(users,indent=2))
        print(f"Name: {sessname}, Title: '{title}'\nContent: {content}")
        return '<meta http-equiv="Refresh" content="0; url=/sendpost" />'

    else:
        return f"{request.method} requests don't work on this url"

@app.route("/channels/")
def channels():
    channel = open("templates/genposts.html", "r").read().replace("^api^","channelget").replace("^counter^","channelcount")
    return renderindex(channel,"Channels",session) 

@app.route("/channelget/<id>")
def channelget(id):
    try:
        return getData("json/catagories.json")[str(id)]
    except IndexError:
        return "null"

@app.route("/channelcount/")
def channelcount():
    return str(len(getData("json/catagories.json")))

# DSI CODE
def DSIrenderindex(page,title,session):
    index = open("templates/dsi/index.html","r").read()
    users = json.loads(open("json/users.json","r").read())
    try:
        userpfp = "/imagedatabase/"+users[session["name"]]["pfp"]+".png"
    except:
        userpfp = "/images/bark-it-small.png"
    user = session.get("name", "Login")
    return index.replace("^posts^",page).replace("^profile^",user).replace("^title^","Bark-IT DSI - "+title).replace("^pfp^",userpfp)
@app.route("/ds/")
def DSIhome():
    start = time()
    posts = open("templates/dsi/dsiposts.html", "r").read()
    end = time()
    processing_time = end - start
    return DSIrenderindex(posts,"Home",session)           
@app.route("/ds/<page>")
def DSIpage(page):
    match page:
        case "post":
            return DSIrenderindex("""<div><center><form action="/sendpost"><label for="id1">Title </label>
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
                                    ,"post",session)
    
        case "login":
            return DSIrenderindex("""
                                    <div>
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
                                    ,"Login",session)
        case "info":
            return "info page"
        case "browse":
            id = request.args.get("postid")
            posts = open("templates/dsi/dsipostbrowse.html", "r").read()
            postjson = json.loads(loadjson()).get(id, "nill")
            if id == None:
                return f'<meta http-equiv="Refresh" content="0; url=/ds/browse?postid={str(len(json.loads(loadjson()))-1)}"/>'
            return DSIrenderindex(posts.replace("^user^",postjson["author"]).replace("^title^",postjson["title"]).replace("^content^",postjson["content"]).replace("^right^",str(int(id)-1)).replace("^left^",str(int(id)+1)),"Browser",session)
    


if __name__ == "__main__":
    app.run("0.0.0.0", 8080)
    app.config['UPLOAD_FOLDER'] = 'imagedatabase'
