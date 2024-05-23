#!/usr/bin/env python3

import os
import json
from pathlib import Path
from hashlib import sha3_512, md5
from mysql.connector import connect, Error
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
host = "0.0.0.0"
port = 2324
debug = False

with open("db_user.json", 'r') as file:
    login_details = json.load(file)

database = "pclub_secy_task"
blog_parts = {"title": 1, "content": 2, "link": 3}

not_allowed_commands = [
    "cat", "ls", "shutdown", "reboot", "rm", "cp", "mv", "dd", "du", ":(){ :|: & };:", "chmod", "mkfs",
    "chown", "echo", "wget", "curl", "git", "tar", "python", "nc", "ssh", "usermod", "iptables", "find",
    "perl", "mkfifo", "sh", "exec", "apt", "sudo", "ftp", "sftp", "touch", "socat", "telnet", "py",
    "html", "css", "js", "grep", ">", ">>", "vi", "vim", "print", "ul"
]
not_allowed_files = ["py", "json", "templates", "git", "md"]
cwd = Path.cwd()

@app.route("/", methods=["GET"])
def indexRoute():
    return render_template("index.html")

@app.route("/gallery", methods=["GET"])
def galleryRoute():
    image_files = os.listdir("static/images/gallery")
    image_data = [{"src": f"/getFile?file={str(cwd)}/static/images/gallery/{image_file}"} for image_file in image_files]
    return render_template("gallery.html", images=image_data)

@app.route("/blogs", methods=["GET"])
def blogsRoute():
    return render_template("blogs.html")

@app.route("/ipDetails", methods=["GET", "POST"])
def ipDetailsRoute():
    if request.method == "GET":
        return render_template("ip_tracking.html")
    else:
        ip = request.json["ip"]
        for command in not_allowed_commands:
            if command in ip:
                return {"commandOutput": "Not Allowed"}
        commandOutput = os.popen(f"./ip_details.py {ip}").read()
        return {"commandOutput": commandOutput.split('\n')}

@app.route("/secretary_login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        password = md5(request.form["password"].encode()).hexdigest()
        connection = connect(host="localhost", user=login_details["user"], password=login_details["password"])
        cursor = connection.cursor()
        cursor.execute(f"USE {database}")
        cursor.execute(f"SELECT password FROM USERS WHERE userhash='{sha3_512(user.encode()).hexdigest()}'")
        original_password = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(original_password) == 1:
            original_password = original_password[0][0]
            if original_password == password:
                return render_template("file.html", user=user)
            else:
                return render_template("login.html", message="Incorrect Password")
        else:
            return render_template("login.html", message="User Not Found")
    return render_template("login.html")

@app.route("/recovery", methods=["GET"])
def recoveryRoute():
    return render_template("recovery.html")

@app.route("/robots.txt", methods=["GET"])
def robotsRoute():
    return render_template("robots.html")

@app.route("/getFileList", methods=["GET"])
def getFileList():
    user = request.args.get("user")
    users = os.listdir("static/files")
    if user not in users:
        return []
    else:
        files = os.listdir(f"static/files/{user}")
        return files

@app.route("/getFile", methods=["GET"])
def getFileRoute():
    file_name = request.args.get("file")
    for file in not_allowed_files:
        if file in file_name:
            return "Not Allowed", 403
    with open(file_name, 'rb') as file:
        content = file.read()
    return content, 200

@app.route("/download", methods=["GET"])
def downloadRoute():
    user_file = request.args.get("file")
    if ".." in user_file or user_file.startswith('/'):
        return '', 403
    else:
        return send_file(f"static/files/{user_file}", as_attachment=True)

@app.route("/getBlogDetail", methods=["GET"])
def getBlogDetailRoute():
    blog_index = request.args.get("blog")
    blog_part = request.args.get("part")
    connection = connect(host="localhost", user=login_details["user"], password=login_details["password"])
    cursor = connection.cursor()
    cursor.execute(f"USE {database}")
    cursor.execute(f"SELECT * FROM BLOGS WHERE id='{blog_index}'")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    result = result[0][blog_parts[blog_part]]
    return result

if __name__ == "__main__":
    app.run(host=host, port=port, debug=debug)
