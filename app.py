import os
import sqlite3
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
#from flask_session import Session
#from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


# Configure application
app = Flask(__name__)
app.secret_key = "hutthjswdcnaouyv"
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///markers.db")


#index route used to render index.html
@app.route("/")
def index():
    return render_template("index.html")
#@app.route("/index" , methods= ["POST", "GET"])
#def index2():
    #return render_template("map.html")


#the route containing code to add location

@app.route("/trash", methods=["GET", "POST"])
def trash():

    #get the coordinates from from in map.html
    if request.method == "POST":

        lat = request.form.get("lat")
        long = request.form.get("long")

        #if no data redirect to route/map
        if lat == '' or long == '' :
            return redirect ("/map")
        else:

            #if data avilable add to database
            number_id=db.execute("INSERT INTO markers (long , lat) VALUES(?, ?)", long, lat)
            print(number_id)
            #
            session['number_id'] = number_id
            return render_template("trash.html")

#delete emty columns, load markers
@app.route("/map", methods=["GET", "POST"])
def map():
    #deleting rows with emoty columns
    conn = sqlite3.connect('markers.db')
    cursor = conn.cursor()
    sql = f"DELETE FROM markers WHERE long IS NULL OR lat IS NULL OR image IS NULL"
    cursor.execute(sql)
    conn.commit()

    #displaying the database on map
    conn = sqlite3.connect('markers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, lat, long, image  FROM markers")
    coor = cursor.fetchall()
    conn.close()

    return render_template("map.html", coor = coor)


#for adding images
@app.route("/sucess", methods = ["POST", "GET"])
def sucess():
    if request.method == "POST":
        #get user image
        trashpic = request.files.get("trashpic")
        #get number id as in /trash
        number_id = session.get('number_id')
        #if user clicked on
        nopic= request.form.get("nopic")

        print(number_id)

        #if user has clicked
        if nopic == "1":
            #populate image column with image in static folder
            db.execute("UPDATE markers SET image = ? WHERE id = ?", "static/constImg/noimg.png", number_id)
            return redirect ("/map")
        #if trashpic contains a file
        elif trashpic != None:
            ##used AI in helping with code
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

            def allowed_file(filename: str) -> bool:
                #Check if the file has an allowed extension.
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            ##End of AI copied


            #create name for image
            #get file name and name in a way safe to save on system
            safe_name = secure_filename(trashpic.filename)
            #add the number id to make unique
            safe_name = "trash"+ str(number_id) + safe_name
            print(safe_name)

            #save image in folder
            if allowed_file(safe_name):
                save_path = os.path.join("static/uploads", safe_name)
                print(f"Safe to save at: {save_path}")
                trashpic.save(save_path)
                #update database image column with file path
                db.execute("UPDATE markers SET image = ? WHERE id = ?", save_path, number_id)
                return redirect ("/map")
            else:
                #reload map
                print(f"File '{safe_name}' has a disallowed extension.")
                
                return redirect ("/map")



#deleting markers
@app.route("/clean", methods=["POST"])
def clean():
     #get id of button clciked
     if request.method == "POST":
        #AI was used to look at sample codes on how to use get_jason
        buttonId = request.get_json()
        print(buttonId)
        print("helloe")
        #connect to database

        conn = sqlite3.connect('markers.db')

        #getting the image path
        cursor = conn.cursor()
        cursor.execute("SELECT image FROM markers WHERE id = ?", (buttonId["id"],))
        image_path = cursor.fetchone()
        print(image_path)
        #when path is NOT of static image
        if  image_path[0] != "static/constImg/noimg.png":
            #delete image
            os.remove(image_path[0])
            #delete row from databse
            sql = f"DELETE FROM markers WHERE id = ?"
            cursor.execute(sql, (buttonId["id"],))
            conn.commit()
            return redirect ("/map")
        else:
            #when it is static image
            #delete row in databse
            sql = f"DELETE FROM markers WHERE id = ?"
            cursor.execute(sql, (buttonId["id"],))
            conn.commit()
            return redirect ("/map")

