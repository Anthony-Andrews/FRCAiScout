from app import app, sock
from flask import request, render_template, send_file
import modelrun
import random
import zipfile
import os

files = {}

@app.route('/', methods=["POST", "GET"])
def index():
    print(request.form)
    if request.method == "GET":
        return render_template("index.html")
    else:
        name = '%030x' % random.randrange(16**30)
        request.files['vide1o'].save(name)
        points = request.form.get("points").split(",")
        #points = [(points[2*i+1], points[2*i]) for i in range(4)] #bool(request.form.get("offset"))
        modelrun.run(name, int(request.form.get("quality")))
        # with zipfile.ZipFile("temp.zip", "w") as a:
        #     a.write("output.mp4")
        os.remove(name)
        return send_file("../temp.zip")
    
    #flip overlay
    #robot 5


        