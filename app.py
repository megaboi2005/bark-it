"""
    Bark-It source code, IDK change this to what you like.
"""

# Imports
import cryptocode
import random
import json
import time
import os

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
    session
)

from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from Levenshtein import distance

global post

post = open("templates/post.html", "r").read()
app = Flask(__name__, static_url_path="/files", static_folder="static")
app.secret_key = b'super_secret_key'


def get_post_json() -> str:
    """
        Loads the post json file
    """
    with open("json/posts.json", "r") as file:
        return file.read()


def get_json_data(file: str) -> dict | list:
    """
        Gets the json data from {file}
    """
    return json.loads(open(file, "r").read())


def check_if_banned(user: str) -> bool:
    """
        LAG WARNING!
        Returns a boolean value depending on if a user is banned or not
    """
    with open("json/users.json", "r") as file:
        users = json.load(file)

    return users[user].get("banned")


def render_index(page: str, title: str, session) -> str:
    """
        Returns a index page template.
    """
    with open("json/users.json", "r") as file:
        users = json.load(file)

    profile_picture = "/imagedatabase/" + users[session["name"]]["pfp"]

    with open("templates/index.html","r") as file:
        index = file.read()

    return (
        index
        .replace("^posts^", page)
        .replace("^profile^", session.get("name", "Login"))
        .replace("^title^", "Bark-IT - " + title)
        .replace("^pfp^", profile_picture)
    )


def get_user_profile_picture(user):
    """
        Returns the path to a user's profile picture.
    """
    with open("json/users.json", "r") as file:
        users = json.load(file)

    try:
        return "/imagedatabase/" + users[user]["pfp"]
    except:
        return "/imagedatabase/0.png"

def makepost(name,request):
    title = request.args.get("title")
    content = request.args.get("post")
    if title == None or content == None:
        return "do not make an empty post"
    posts = get_json_data("json/posts.json")
    users = get_json_data("json/users.json")
    newPostId = max(map(int, posts.keys())) + 1
    postfile = open("json/posts.json", "w")
    usersfile = open("json/users.json","w")
    posts.update(
        {
            newPostId: {
                "title": title,
                "author": name,
                "content": content.replace("<","&lt;").replace(">","&gt;"),
                "likes": 1,
                "locked": False,
                "comments": {},
                "time" : time.time()
            }
        }
    )
    length = len(users[session["name"]]["posts"])
    users[session["name"]]["posts"].update(
        {length: {"id":str(newPostId)}}
    )
    postfile.write(json.dumps(posts, indent=2))
    usersfile.write(json.dumps(users,indent=2))
    print(f"Name: {name}, Title: '{title}'\nContent: {content}")
    #postsfile.close()
    #usersfile.close()

def makecomment(name, request):
    content = request.args.get("content")
    post = request.args.get("post")
    if content == None:
        return "do not make an empty comment"
    if check_if_banned(name):
        return "you are banned"
    users = get_json_data("json/users.json")
    posts = get_json_data("json/posts.json")
    newCommentId = len(posts[post]["comments"])
    postfile = open("json/posts.json", "w")
    posts[post]["comments"].update(
        {
            newCommentId: {
                "author": name,
                "content": content.replace("<","&lt;").replace(">","&gt;"),
                "likes": 1,
                "locked": False,
                "comments": {},
            }
        }
    )
    postfile.write(json.dumps(posts, indent=2))
    postfile.close()


@app.route("/")
def main(name=None):
    global processing_time
    global posts
    with open("templates/genposts.html", "r") as load:
        posts = load.read().replace("^api^","postget?arg=").replace("^counter^","/api/postcount")
    user_agent = request.headers.get('User-Agent')
    #print(user_agent.split('(')[1].split(')')[0])
    return render_index(posts, "Home", session)


@app.route("/user/<name>")
def userpage(name):
    if name == None:
        return "invalid user"
    with open("templates/genposts.html", "r") as load:
        posts = load.read().replace("^api^","userget?arg="+name+"&id=").replace("^counter^","/api/postcountuser?arg="+name)
    users = json.loads(open("json/users.json","r").read())
    try:
        return render_index(posts,name,session) + open("templates/profile.html", "r").read().replace("^pfp^",get_user_profile_picture(name)).replace("^profile^",name).replace("^bio^",users[name]["bio"])
    except KeyError:
        return render_index(posts,name,session) + open("templates/profile.html", "r").read().replace("^pfp^",get_user_profile_picture(name)).replace("^profile^",name).replace("^bio^","Hello World")


@app.route("/api/<api>")
def api(api):
    arg = request.args.get("arg")
    match api:
        case "postcountuser":
            return str(len(get_json_data("json/users.json")[arg]["posts"]))
        case "userget":
            postid = request.args.get("id")
            try:
                return json.loads(get_post_json())[get_json_data("json/users.json")[arg]["posts"][postid]["id"]]
            except KeyError:
                return "null"

        case "getprofile":
            return get_user_profile_picture(arg)
        case "postget":
            post = json.loads(get_post_json()).get(arg, "nill")
            if post == "nill":
                return "nill"
            #print('{"author":"'+post["author"]+'", "content":"'+post["content"]+'","title":"'+post["title"]+'"}')
            try: 
                return {"author":post["author"],"content":post["content"],"title":post["title"],"time":post["time"]}
            except KeyError:
                return {"author":post["author"],"content":post["content"],"title":post["title"]}
        case "postcount":
            return str(len(json.loads(get_post_json())))
            
        case "makepost":
            userread = json.loads(open("json/users.json", "r").read())
            name = request.args.get("name")
            password = request.args.get("pass")
            if name == None or password == None:
                return "provide a name or password when making an api post"
            else:
                try:
                    if check_if_banned(name):
                        return "you are banned"
                except KeyError:
                    return "provide an EXISTING name please"
                decrypt = cryptocode.decrypt(userread[name]["password"], password)
                if decrypt == password:
                    makepost(name,request)
                    return 
                else:
                    return "provide a CORRECT name or password when making an api post"
        case "sendpost":
            sessname = session.get("name")
            if sessname:
                if check_if_banned(sessname):
                    return "you are banned"
            else:
                return render_index("not logged in","Post",session)
            
            title = request.args.get("title")
            content = request.args.get("post")
            if title == None or content == None:
                return "No title or content isn't allowed in posts"       
            if len(content) > 6000 or len(title) > 6000:
                return "post size is too big"
            makepost(sessname,request)
            if request.args.get("device") == None:
                return '<meta http-equiv="Refresh" content="0; url=/" />'
            elif request.args.get("device") == "dsi":
                return '<meta http-equiv="Refresh" content="0; url=/ds" />'
        case "sendcomment":
            name = session.get("name")
            makecomment(name,request)
            return "<meta http-equiv=\"Refresh\" content=\"0; url=/\" />"
        case "comget":
            identifier = request.args.get("id")
            return json.loads(open("json/posts.json","r").read())[str(arg)]["comments"][str(identifier)]
        case "comcount":
            return str(len(json.loads(open("json/posts.json","r").read())[str(arg)]["comments"]))
            
@app.route("/comments/<post>")
def commentdisplay(post):
    posts = open("templates/genposts.html", "r").read().replace("^api^",f"comget?arg={post}&id=").replace("^counter^","/api/comcount?arg="+post).replace("mode = 0","mode = 1")
    return render_index(posts,"Home",session)

@app.route("/images/<path:filename>")
def images(filename):

    if filename == "bark-it.png":
        chance = random.randrange(1, 1000)
        print(chance)
        if chance == 69:
            return send_from_directory("images", "meow-it.png", as_attachment=True)
    if filename == "bark-it-small.png":
        chance = random.randrange(1, 1000)
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
    return render_index(open("templates/about.html").read(),"About",session)

@app.route("/login/")
def login():
    userread = json.loads(open("json/users.json", "r").read())
    name = request.args.get("name")
    password = request.args.get("pass")
    
    if name == None or password == None:
        return "You must have the username and password to be able to login"
    else:
        try:
            if check_if_banned(name):
                return "you are banned"
        except KeyError:
            return '<meta http-equiv="Refresh" content="0; url=/" /> <p>incorrect username or password</p>'
        decrypt = cryptocode.decrypt(userread[name]["password"], password)
        # if decrypt == False:
        # return  open("templates/index.html","r").read().replace("^profile^",sessname).replace("^posts^","<center><p>incorrect username or password</p></center> "+form)
        if decrypt == password:
            session["name"] = name
        else:
            return '<meta http-equiv="Refresh" content="0; url=/" /> <p>incorrect username or password</p>'
        return '<meta http-equiv="Refresh" content="0; url=/" />'
    


@app.route("/register/")
def register():
    sessname = session.get("name", "Login")
    userread = json.loads(open("json/users.json", "r").read())
    name = request.args.get("name")
    password = request.args.get("pass")

    if name == None or password == None:
        return "You must have the username and password to be able to register"
    for item in userread:
        if name == item:
            return render_index("<p>Name already taken</p> ","Register",session)
    password = cryptocode.encrypt(password, password)
    userwrite = open("json/users.json", "w")
    
    userread.update(
        {
            name : {
                "password": password, 
                "bio" : "Hi, I'm new!",
                "banned": False,
                "posts": {},
                "pfp": "0.png"
                }
            
        }
    
    )

    userwrite.write(json.dumps(userread,indent=2))
    return '<meta http-equiv="Refresh" content="2; url=/"/>'


@app.route("/settings/")
def settings():
    sessname = session.get("name", "Login")
    if sessname == "admin":
        return render_index(open("templates/settingsadmin.html", "r").read(),"Admin Settings",session)
    return render_index(open("templates/settings.html", "r").read(),"Settings",session)


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
        case "changebio":
            bio = request.args.get("bio")
            if bio == "":
                return '<meta http-equiv="Refresh" content="0; url=/" />'
            users = json.loads(open("json/users.json","r").read())
            users[sessname]["bio"] = bio
            with open("json/users.json","w") as userwrite:
                userwrite.write(json.dumps(users,indent=2))
                return '<meta http-equiv="Refresh" content="0; url=/" />'
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
                return render_index(postsrender,searched,session)
    else:
        return render_index(open("templates/search.html", "r").read(),"Search",session)

#@app.route("/post/<id>")
#def postdisplay(id):


@app.route("/imagedatabase/<path:filename>")
def profiledatabase(filename):
    try:
        return send_from_directory("imagedatabase", filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/uploadprofile', methods=['POST'])
def uploadpfp():
    supported_extensions = ["apng","avif","gif","jpg","jpeg","jfif","pjpeg","pjp","png","svg","webp"]
    if session.get("name","nope") == "nope":
        return '<meta http-equiv="Refresh" content="0; url=/"/>'
    f = request.files['file']
    userread = get_json_data("json/users.json")
    
    extension = f.filename.split(".")[len(f.filename.split("."))-1]
    f.filename.split(".")[len(f.filename.split("."))-1]
    if not extension in supported_extensions:
        return "extension isn't supported!"
    if  userread[session["name"]]["pfp"] == "0":
        userwrite = open("json/users.json","w")
        f.save(os.path.join("imagedatabase", str(len(os.listdir("imagedatabase")))+"."+extension))
        userread[session["name"]]["pfp"] = str(len(os.listdir("imagedatabase"))-1) + "."+extension
        userwrite.write(json.dumps(userread,indent=2))
    else:
        if not userread[session["name"]]["pfp"].split(".")[len(userread[session["name"]]["pfp"].split("."))-1] == extension:
            userwrite = open("json/users.json","w")
            f.save(os.path.join("imagedatabase", str(len(os.listdir("imagedatabase")))+"."+extension))
            userread[session["name"]]["pfp"] = str(len(os.listdir("imagedatabase"))-1) + "."+extension
            userwrite.write(json.dumps(userread,indent=2))
            return '<meta http-equiv="Refresh" content="0; url=/"/>'
        f.save(os.path.join("imagedatabase", userread[session["name"]]["pfp"]))
    return '<meta http-equiv="Refresh" content="0; url=/"/>'



## broken so I might as well not port to the api
@app.route("/channels/")
def channels():
    channel = open("templates/genposts.html", "r").read().replace("^api^","channelget").replace("^counter^","channelcount")
    return render_index(channel,"Channels",session) 

##@app.route("/channelget/<id>")
##def channelget(id):
##    try:
##        return get_json_data("json/catagories.json")[str(id)]
##    except IndexError:
##        return "null"
##
##@app.route("/channelcount/")
##def channelcount():
##    return str(len(get_json_data("json/catagories.json")))

# DSI CODE
def dsi_render_index(page,title,session):
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
    return dsi_render_index(posts,"Home",session)           
@app.route("/ds/<page>")
def DSIpage(page):
    match page:
        case "post":
            return dsi_render_index("""<div><center><form action="/sendpost"><label for="id1">Title </label>
                                            <br>
                                            <input class=input type="text" id="id1" name="title" required>
                                            <br>
                                            <label for="id2">Content  </label>
                                            <br>
                                            <textarea class=input style="resize: vertical;" rows=10 maxlength="6000" id="id2" name="post" required></textarea>
                                            <br>
                                            <input class=styledbutton style="width: 30%; height: 50%;" type="submit" value="Submit">
                                            <br>
                                            <select name="device" id="device">
                                                <option value="dsi">DSI</option>
                                            </select>
                                        </form>
                                        </center>
                                    </div>"""
                                    ,"post",session)
    
        case "login":
            return dsi_render_index("""
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
            postjson = json.loads(get_post_json()).get(id, "nill")
            if id == None:
                return f'<meta http-equiv="Refresh" content="0; url=/ds/browse?postid={str(len(json.loads(get_post_json()))-1)}"/>'
            return dsi_render_index(posts.replace("^user^",postjson["author"]).replace("^title^",postjson["title"]).replace("^content^",postjson["content"]).replace("^right^",str(int(id)-1)).replace("^left^",str(int(id)+1)),"Browser",session)
    


if __name__ == "__main__":
    app.run("localhost", 19142)
    app.config['UPLOAD_FOLDER'] = 'imagedatabase'
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1000 * 1000
