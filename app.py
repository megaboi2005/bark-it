import json
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
from werkzeug.utils import secure_filename
import os
from urllib.parse import urlparse
import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
global post

# I suggest commenting these out after they are done downloading

nltk.download('stopwords')

nltk.download('punkt')

nltk.download('averaged_perceptron_tagger')



post = open("templates/post.html", "r").read()
app = Flask(__name__,static_url_path='/files',static_folder='static')
app.secret_key = b"secretkey"




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

def getData(file):
    """Gets the json data from {file}"""
    return json.loads(open(file, "r").read())


def checkban(user):
    userread = json.loads(open("json/users.json", "r").read())
    if not userread[user]:
        return 0
    return userread[user]["banned"]

def renderindex(page,title,session):
    version = "Alpha 0.9"
    try:
        users = json.loads(open("json/users.json","r").read())
        theme = users[session["name"]].get("theme","normal.html")
        if not os.path.isfile("templates/themes/"+theme):
            theme = "normal.html"
    except:
        theme = "normal.html"
    with open("templates/themes/"+theme,"r") as index:
        try:
            userpfp = "/imagedatabase/"+users[session["name"]]["pfp"]
        except:
            userpfp = "/images/bark-it-small.png"
        user = session.get("name", "Login")
        return index.read().replace("^posts^",page).replace("^profile^",user).replace("^title^","Bark-IT - "+title).replace("^pfp^",userpfp).replace("^version^",version)


def getuserprofile(user):
    try:
        users = json.loads(open("json/users.json","r").read())
        extension = users[user]["pfp"].split(".")[len(users[user]["pfp"].split("."))-1]
        print("/imagedatabase/"+users[user]["pfp"])
        return "/imagedatabase/"+users[user]["pfp"]
    except KeyError:
        return "/imagedatabase/0.png"

def usermod(user,item,arg):
    users = json.loads(open("json/users.json","r").read())
    try:
        users[user][item] = arg
    except KeyError:
        return False
    with open("json/users.json","w") as userwrite:
        userwrite.write(json.dumps(users,indent=2))
        return True

def getreason(name):
    return renderindex("<div class=posts><p> you are banned for the reason:" +json.loads(open("json/users.json","r").read())[name]["reason"] ,"Banned", {}) + "</p></div>"
    

def makepost(name,request):
    title = request.args.get("title")
    content = request.args.get("post")
    if title == None or content == None:
        return "do not make an empty post"
#    posts = getData("json/posts.json")
    users = getData("json/users.json")
    newPostId = str(len(os.listdir("json/posts")))
    post = json.loads("{}")
    os.makedirs("json/posts/"+newPostId+"/comments")

    postfile = open("json/posts/"+newPostId+"/postdat.json", "w")
    usersfile = open("json/users.json","w")
    post.update(
        {
                "title": title,
                "author": name,
                "content": content.replace("<","&lt;").replace(">","&gt;"),
                "likes": 1,
                "locked": False,
                "time" : time.time(),
                "attachments": {}
        }
    )
    length = len(users[session["name"]]["posts"])
    users[session["name"]]["posts"].update(
        {length: {"id":str(newPostId)}}
    )
    postfile.write(json.dumps(post, indent=2))
    usersfile.write(json.dumps(users,indent=2))
    with open("json/searchmap.json","r") as smap:
        searchmap = json.loads(smap.read())
        tokens = word_tokenize(content)
        tagged_tokens = pos_tag(tokens)
        topic_words = []
        seen_words = set()
        for word, pos in tagged_tokens:
            if (pos.startswith('NN') or pos.startswith('NNP')) and word.lower() not in seen_words:
                topic_words.append(word)
                seen_words.add(word.lower())
        for a in topic_words:
            try:
                searchmap[a.lower()].insert(0,newPostId)
            except KeyError:
                searchmap[a.lower()] = [newPostId]
        searchwrite = open("json/searchmap.json","w").write(json.dumps(searchmap))

    print(f"Name: {name}, Title: '{title}'\nContent: {content}")

def makecomment(name,request):
    content = request.args.get("content")
    post = request.args.get("post")
    if content == None:
        return "do not make an empty comment"
    if checkban(name):
        return getreason(name)
    newComId = str(len(os.listdir("json/posts/"+post+"/comments")))
    print("yes - json/posts/"+post+"/comments/"+newComId+".json")
    comment = json.loads("{}")
    comfile = open("json/posts/"+post+"/comments/"+newComId+".json", "x")
    comment.update(
        {
            "author": name,
            "content": content.replace("<","&lt;").replace(">","&gt;"),
            "likes": 1,
            "locked": False,
        }
    )
    comfile.write(json.dumps(comment, indent=2))
    comfile.close()
@app.route("/")
def main(name=None):
    global processing_time
    global posts
    with open("templates/genposts.html", "r") as load:
        posts = load.read().replace("^api^","postget?arg=").replace("^counter^","/api/postcount")
    user_agent = request.headers.get('User-Agent')
    return renderindex(posts,"Home",session)

@app.route("/random")
def random():
    global processing_time
    global posts
    with open("templates/randomgen.html", "r") as load:
        posts = load.read().replace("^api^","postget?arg=").replace("^counter^","/api/postcount")
    user_agent = request.headers.get('User-Agent')
    return renderindex(posts,"Random",session)


@app.route("/user/<name>")
def userpage(name):
    if name == None:
        return "invalid user"
    users = json.loads(open("json/users.json","r").read())
    with open("templates/profile.html", "r") as load:
        posts = load.read().replace("^api^","userget?arg="+name+"&id=").replace("^counter^","/api/postcountuser?arg="+name).replace("^pfp^",getuserprofile(name)).replace("^profile^",name).replace("^bio^",users[name]["bio"])

    try:
        return renderindex(posts,name,session)
    except KeyError:
        return renderindex(posts,name,session) + open("templates/profile.html", "r").read().replace("^pfp^",getuserprofile(name)).replace("^profile^",name).replace("^bio^","Hello World")

@app.route("/api/<api>")
def api(api):
    arg = request.args.get("arg")
    match api:
        case "postcountuser":
            return str(len(getData("json/users.json")[arg]["posts"]))
        case "userget":
            postid = request.args.get("id")
            try:
                post = json.loads(open("json/posts/"+getData("json/users.json")[arg]["posts"][postid]["id"]+"/postdat.json","r").read())
                return {"author":post["author"],"content":post["content"],"title":post["title"],"time":post["time"]}
            except KeyError:
                return "null"

        case "getprofile":
            return getuserprofile(arg)
        case "postget":
            try:
                post = json.loads(open("json/posts/"+arg+"/postdat.json","r").read())
            except FileNotFoundError:
                return "null"
            if post == "nill":
                return "nill"
            try: 
                return {"author":post["author"],"content":post["content"],"title":post["title"],"time":post["time"]}
            except KeyError:
                return {"author":post["author"],"content":post["content"],"title":post["title"]}
        case "postcount":
            return str(len(os.listdir("json/posts")))
            
        case "makepost":
            userread = json.loads(open("json/users.json", "r").read())
            name = request.args.get("name")
            password = request.args.get("pass")
            if name == None or password == None:
                return "provide a name or password when making an api post"
            else:
                try:
                    if checkban(name):
                        return getreason(name)
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
                if checkban(sessname):
                    return getreason(sessname)
            else:
                return renderindex("not logged in","Post",session)
            
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
            
            try:
                identifier = request.args.get("id")
                return json.loads(open("json/posts/"+str(arg)+"/comments/"+str(int(identifier))+".json","r").read())
            except FileNotFoundError:
                return "null"
        case "comcount":
            return str(len(os.listdir("json/posts/"+str(arg)+"/comments")))
            
@app.route("/comments/<post>")
def commentdisplay(post):
    posts = open("templates/genposts.html", "r").read().replace("^api^",f"comget?arg={post}&id=").replace("^counter^","/api/comcount?arg="+post).replace("mode = 0","mode = 1")
    return renderindex(posts,"Home",session)

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
    userread = json.loads(open("json/users.json", "r").read())
    name = request.args.get("name")
    password = request.args.get("pass")
    
    if name == None or password == None:
        return "You must have the username and password to be able to login"
    else:
        try:
            if checkban(name):
                return getreason(name)
        except KeyError:
            return '<meta http-equiv="Refresh" content="0; url=/" /> <p>incorrect username or password</p>'
        decrypt = cryptocode.decrypt(userread[name]["password"], password)
        if decrypt == password:
            session["name"] = name
        else:
            return '<meta http-equiv="Refresh" content="0; url=/" /> <p>incorrect username or password</p>'
        return '<meta http-equiv="Refresh" content="0; url=/" />'
    
@app.route("/logout")
def logout():
    session.clear()
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
            return renderindex("<p>Name already taken</p> ","Register",session)
    password = cryptocode.encrypt(password, password)
    userwrite = open("json/users.json", "w")
    
    userread.update(
        {
            name : {
                "password": password, 
                "bio" : "",
                "banned": 0,
                "theme": "normal.html",
                "posts": {},
                "pfp": "0.png",
                "admin": 0
            }
            
        }
    
    )

    userwrite.write(json.dumps(userread,indent=2))
    return '<meta http-equiv="Refresh" content="2; url=/"/>'


@app.route("/settings/")
def settings():
    sessname = session.get("name", "Login")
    adminstat = json.loads(open("json/users.json").read())[sessname].get("admin",0)
    if adminstat:
        return renderindex(open("templates/settingsadmin.html", "r").read(),"Admin Settings",session)
    elif not adminstat:
        return renderindex(open("templates/settings.html", "r").read().replace("^profile^",getuserprofile(sessname)),"Settings",session)
    else:
        return '<meta http-equiv="Refresh" content="0; url=/" />'
        

@app.route("/chngsetting/<setting>")
def chngsettings(setting):
    try:
        sessname = session["name"]
    except:
        return "please log in"
    adminstat = json.loads(open("json/users.json").read())[sessname]["admin"]
    match setting:
        case "changepass":
            password = request.args.get("oldpass")
            newpass = request.args.get("newpass")
            newpass2 = request.args.get("newpass2")
            if not newpass == newpass2:
                return '<meta http-equiv="Refresh" content="2; url=/settings"/><p>new passwords do not match</p>'
            if not len(newpass) >= 1:
                return "put in a new password"
            if cryptocode.decrypt(userread[sessname]["password"], password) == password:
                usermod(sessname,"password",cryptocode.encrypt(newpass, newpass))
                return '<meta http-equiv="Refresh" content="0; url=/" />'
            else:
                return "wrong password"
        case "changebio":
            bio = request.args.get("bio")
            if bio == "":
                return '<meta http-equiv="Refresh" content="0; url=/" />'
            usermod(sessname,"bio",bio)
            return '<meta http-equiv="Refresh" content="0; url=/user/'+sessname+'" />'

        case "changetheme":
            theme = request.args.get("theme")
            if theme == "":
                return '<meta http-equiv="Refresh" content="0; url=/" />'
            usermod(sessname,"theme",theme)
            return '<meta http-equiv="Refresh" content="0; url=/" />'

        case "adminban":
            if adminstat:
                return "you are not an admin"
            user = request.args.get("user", 0)
            reason = request.args.get("reason", 0)
            if not user and reason:
                return "missing parameter"
            usermod(user,"banned",1)
            usermod(user,"reason",reason)
            return "banned"

        case "adminunban":
            if adminstat:
                return "you are not an admin"
            user = request.args.get("user", "no user")
            usermod(user,"banned",0)
            return "unbanned"

        case "admindelpost":
            if adminstat:
                return "you are not an admin"
            identifier = request.args.get("id", 0)
            reason = request.args.get("reason", 0)

            if identifier and reason:
                posts = json.loads(open("json/posts/"+identifier+"/postdat.json","r").read())
                posts["content"] = "{{This post has been deleted for: " + reason +"}}"
                posts["title"] = "{{This post has been deleted for: "+ reason + "}}"
                with open("json/posts/"+identifier+"/postdat.json", "w") as postwrite:
                    postwrite.write(json.dumps(posts, indent=2))
                return "deleted post"
            else:
                return "missing parameter"
        case "adminadd":
            if sessname == "admin":
                name = request.args.get("name", 0)
                if not name:
                    return "doesn't exist"
                user = json.loads(open("json/users.json").read())
                user[name]["admin"] = 1
                with open("json/users.json","w") as userwrite:
                    userwrite.write(json.dumps(user))
                return "admin'd"
            return "must be the admin account to do such a task"

        case "adminrem":
            if sessname == "admin":
                name = request.args.get("name", 0)
                if not name:
                    return "doesn't exist"
                user = json.loads(open("json/users.json").read())
                user[name]["admin"] = 0
                with open("json/users.json","w") as userwrite:
                    userwrite.write(json.dumps(user))
                return "admin'nt"
            return "must be the admin account to do such a task"

@app.route("/search/")
def searchpage():
    sessname = session.get("name", "Login")
    typeof = request.args.get("object")
    searched = request.args.get("search")
    if not searched == None and not typeof == None:
        match typeof:
            case "channel":
                channellist = []
                channels = json.loads(open("json/catagories.json", "r").read())
                for i in range(len(channels)):
                    if distance(searched, channels[str(i)]["name"]) < 4:
                        channellist.append(channels[str(i)]["name"])
                return channellist
            case "posts":
                search = searched.lower()
                tokens = word_tokenize(search)
                tagged_tokens = pos_tag(tokens)
                topic_words = [word for word, pos in tagged_tokens if pos.startswith('NN') or pos.startswith('NNP')]
                
                with open("json/searchmap.json","r") as smap:
                    searchmap = json.loads(smap.read())
                    output = "<div class=posts>"
                    posts = []
                    for i in topic_words:
                        mapped = searchmap.get(i,[])
                        loop = 0
                        if len(mapped) > 20:
                            loop = 20
                        else:
                            loop = len(mapped)
                        for a in range(loop):
                            if len(mapped[a]) == 0:
                                continue
                            else:
                                post = json.loads(open("json/posts/"+mapped[a]+"/postdat.json","r").read())
                                if mapped[a] in posts:
                                    continue
                                posts.append(mapped[a])
                                output += f'<div class=post><a href=/user/{post["author"]}><img style="width:5%; height:auto; position: absolute; top: 6%; left: 0%;" class=logo src="{getuserprofile(post["author"])}"></a><p style="position: absolute; left:6%;">Posted by {post["author"]}</p><br><br><br><br><center><textarea class=name rows="2"   readonly>{post["title"]}</textarea><br><textarea style="resize: vertical;" readonly class=textpost rows=\"5\">{post["content"]}</textarea><br><br><a href=/comments/{str(mapped[a])}><img src="/images/list.png" style="width:3%; left:4%; position: absolute;"></a><img src="/images/reply.png" style="width:3%; float:left" onclick="reply({str(mapped[a])})"><br><br><br><br></center></div>'
                    output += "</div>"
                    return renderindex(output,"h",session)


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
    userread = getData("json/users.json")
    extension = f.filename.split(".")[len(f.filename.split("."))-1]
    f.filename.split(".")[len(f.filename.split("."))-1]
    if not extension in supported_extensions:
        if len(f.filename) == 0:
             return '<meta http-equiv="Refresh" content="0; url=/settings"/>'
        return "extension isn't supported!"
    if  userread[session["name"]]["pfp"] == "0":
        f.save(os.path.join("imagedatabase", session["name"]+"."+extension))
        usermod(session["name"],"pfp",session["name"]+"."+extension)
        return '<meta http-equiv="Refresh" content="0; url=/"/>'
    try:
        os.remove("imagedatabase/"+userread[session["name"]]["pfp"])
    except:
        pass
    f.save(os.path.join("imagedatabase", session["name"]+"."+extension))
    usermod(session["name"],"pfp",session["name"]+"."+extension)
    return '<meta http-equiv="Refresh" content="0; url=/"/>'



## broken so I might as well not port to the api
@app.route("/channels/")
def channels():
    channel = open("templates/genposts.html", "r").read().replace("^api^","channelget").replace("^counter^","channelcount")
    return renderindex(channel,"Channels",session)

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
                                            <br>
                                            <select name="device" id="device">
                                                <option value="dsi">DSI</option>
                                            </select>
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
    app.run("0.0.0.0", 80)
    app.config['UPLOAD_FOLDER'] = 'imagedatabase'
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1000 * 1000
