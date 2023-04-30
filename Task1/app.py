from flask import Flask, request, flash 
from werkzeug.utils import secure_filename
import json
import os
import mariadb
from random import randint
from datetime import datetime,date
app = Flask(__name__)

BASEURI = '/api/v3/app'
app.config['UPLOAD_FOLDER'] = './uploads/'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
data = []
@app.route(BASEURI + '/events',methods = ["GET","POST"])
@app.route(BASEURI + '/events/<id>', methods=["PUT", "DELETE"])
def index(id = 0):
    res_data = {}
    if request.method == 'GET':
        list_event_id = request.args.get('id',type = int)
        page_count = request.args.get('page',type=int)
        event_type = request.args.get('type',type=str)
        limit = request.args.get('limit',type=int)
        
        if event_type and page_count and limit:
            res_data = getEvents(event_type,page_count,limit)
        elif list_event_id:
            res_data = getEventById(list_event_id)
        return json.dumps(res_data, default=json_serial) 
    
    elif request.method == "POST":
        img = request.files["img"]
        if img: 
            img_uri = upload_file(img)
        else:
            return "No file found"
        name = request.form["name"]
        tagline = request.form["tagline"]
        schedule = request.form["schedule"]
        description = request.form["description"]
        moderator = request.form["moderator"]
        category = request.form["category"]
        sub_category = request.form["sub_category"]
        rigor_rank = request.form["rigor_rank"]
        event_data = {"uid":'18',"type":'event', "img_uri": img_uri,"name":name,"tagline":tagline,"schedule":schedule,"description":description,"moderator":moderator,"catergory":category,"sub_category":sub_category,"rigor_rank":rigor_rank}
        id = createEvent(event_data)
        return json.dumps({ "id":id})
    
    elif request.method == "PUT":
        img = request.files["img"]
        if img: 
            img_uri = upload_file(img)
        else:
            return "No file found"
        name = request.form["name"]
        tagline = request.form["tagline"]
        schedule = request.form["schedule"]
        description = request.form["description"]
        moderator = request.form["moderator"]
        category = request.form["category"]
        sub_category = request.form["sub_category"]
        rigor_rank = request.form["rigor_rank"]
        uid = request.form["uid"]
        img_uri = upload_file(img)
        event = "event"
        event_data = {"uid":uid, "type":event, "img_uri": img_uri,"name":name,"tagline":tagline,"schedule":schedule,"description":description,"moderator":moderator,"catergory":category,"sub_category":sub_category,"rigor_rank":rigor_rank}
        status = updateEvent(id,event_data)
        return json.dumps(status)
    
    elif request.method == 'DELETE':
        s = deleteEvent(id)
        return json.dumps(s )
    
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file):
        if file.filename == '':
            flash('No selected file')
            return json.dumps({"status":"no file selected"})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = str(randint(1,1000)) + "-" + filename 
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return os.path.join(app.config['UPLOAD_FOLDER'], filename)


def createEvent(data):
    k = list()
    for key in data.keys():
        k.append(key)
    
    k = ",".join(k)

    k = "(" + k +  ")"
    
    v = list()
    for val in data.values():
        val = "'" + val + "'"
        v.append(val)
    v = ",".join(v)
    v = "(" + v +  ")" 
    cur, conn = openDB()
    cur.execute("INSERT INTO events_details {0} VALUES{1}".format(k,v))
    conn.commit()
    id = cur.lastrowid
    closeDB(cur,conn)
    return id



def getEventById(id):
    cur,conn = openDB()
    data = {}
    coloums = ["event_id","name" ,"description" ,"img_uri" ,"uid" ,"catergory","sub_category","moderator","schedule","rigor_rank","type" ,"tagline"]
    cur.execute("SELECT * FROM events_details where id = ?", (id,))
    table_data = cur.fetchone()
    print(table_data)
    for idx in range(len(coloums)):
        data[coloums[idx]] = table_data[idx]
    closeDB(cur,conn)
    return data


def getEvents(event_type,page_count,limit):
    cur, conn  = openDB()
    ls = list()
    
    coloums = ["event_id","name" ,"description" ,"img_uri" ,"uid" ,"catergory","sub_category","moderator","schedule","rigor_rank","type" ,"tagline"]
    if event_type == 'latest':
        if page_count == 1:
            cur.execute("SELECT * from events_details ORDER BY events_details.`schedule` DESC LIMIT ?",(limit,))
    else:
        limit += 5
        cur.execute("SELECT * from events_details ORDER BY events_details.`schedule` DESC LIMIT ?",(limit,))
    
    table_data = cur.fetchall()
    print(table_data)
    
    
    
    for td in table_data:
        data = {}
        for idx in range(len(coloums)):
            data[coloums[idx]] = td[idx]
        ls.append(data)
    closeDB(cur,conn)
    print(ls)
    return ls


def updateEvent(id,data):
    cur,conn = openDB()
    dic = dict()
    key_value_joined  = list()
    keys = list(data.keys())
    values = list(data.values())
    
    for idx in range(len(keys)):
        string = f"{keys[idx]} = '{values[idx]}'"
        key_value_joined.append(string)
    query = ",".join(key_value_joined)
    print(query)
    cur.execute(f"UPDATE events_details SET {query} WHERE id = ?",(id,))
    conn.commit()
    dic["status"] = "Updated" 
    closeDB(cur,conn)
    return dic
    
def deleteEvent(id):
    cur,conn = openDB()
    cur.execute("DELETE FROM events_details WHERE id = ?",(id,))
    conn.commit()
    closeDB(cur,conn)
    return {"status":"done"}

def openDB():
    conn = mariadb.connect(
        user="root",
        password="",
        host="localhost",
        port=3306,
        database="events"

    )

    cur = conn.cursor()

    return cur, conn

def closeDB(cur,conn):
    cur.close()
    conn.close()

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


app.run(port=8080,debug=True)
