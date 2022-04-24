import json
from time import time

from flask import (
    Flask, abort, redirect, render_template, request, send_file,
    send_from_directory, url_for)
from werkzeug.datastructures import ImmutableMultiDict

global post
post = open("templates/post.html", "r").read()
app = Flask(__name__)


def loadjson():
    return open("json/posts.json", "r").read()


def genposts(page):
    output = ""

    for a in range(3):
        print(a)
        pcount = a + int(page)
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
        .replace("{PostID}", id)
    )


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
    return (
        resp.replace("^render^", str(processing_time))
        .replace("^right^", "/posts/1")
        .replace("^left^", "/posts/1")
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
    return (
        resp.replace("^render^", str(processing_time))
        .replace("^right^", str(int(page) + 1))
        .replace("^left^", str(int(page) - 1))
    )


# api
@app.route("/postget/<id>/")
def postget(id):

    try:
        return loadjson()[id]

    except FileNotFoundError:
        abort(404)


@app.route("/comments/<id>/")
def comments(id):
    return render_template("index.html", posts=genpost(id))


@app.route("/sendpost/", methods=["GET", "POST", "DELETE"])
def user():
    if request.method == "POST":
        data = ImmutableMultiDict(request.form)
        print(request.form)

        title = data["title"]
        token = data["token"]
        content = data["content"]
        posts = getData("json/posts.json")
        newPostId = max(map(int, posts.keys())) + 1
        postfile = open("json/posts.json", "w")
        posts.update(
            {
                newPostId: {
                    "title": title,
                    "author": "TESTIFICATE",
                    "content": content,
                    "likes": 1,
                    "locked": False,
                    "comments": {},
                }
            }
        )
        postfile.write(json.dumps(posts, indent=2))
        print(f"Name: 'TESTIFICATE', Title: '{title}'\nContent: {content}")
        return f"{title} {content}"

    elif request.method == "GET":
        return render_template("sendpost.html")
    else:
        return f"{request.method} requests don't work on this url"

if __name__ == "__main__":
    app.run("0.0.0.0", 8080)