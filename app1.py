import os.path
import os
from flask import Flask,jsonify,send_from_directory
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash,check_password_hash
from flask import request
from flask_cors import CORS, cross_origin
import json
from bson import json_util
app=Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['IMAGE_UPLOADS'] = 'images'
uploads_dir = os.path.join(app.instance_path, 'images')

app.config['CLIENT_IMAGES'] = 'images'
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.secretkey="secretkey"

app.config["MONGO_URI"] = "mongodb://localhost:27017/admin"

mongo = PyMongo(app)

mongo.db.user.create_index(
    [("email", 1), ("name",-1)],
    unique=True
)
mongo.db.adminn.create_index(
    [("email", 1), ("name",-1)],
    unique=True
)
@app.route('/user/login',methods=['POST'])
def logins():
    data = request.json
    _email=data['email']
    _password=data['password']

    if _email and _password and request.method=='POST':
        id = mongo.db.user.find_one({"email":_email})
        userss=dumps(id)
        resp=json.loads(userss)
        t=json.loads(json_util.dumps(id))
        print(t)
        try:
            t1=t['_id']['$oid']
            t['_id']=t1
            print(resp)
            if check_password_hash(resp['password'],_password):
                return {'user':[t],'message':'successfully verified'}
            else:
                return jsonify(resp['password'],_password)
        except:
            return {'message':'error'}
    else:
        return jsonify("error")

@app.route('/user/signup',methods=['POST'])
def upload():
    try:
        if request.method=='POST':
            t=request.files['image']
            username= request.form["username"]
            email= request.form["email"]
            rollno= request.form["rollno"]
            password= generate_password_hash(request.form["password"])
            mentor= request.form["mentor"]
            image = request.files['image']
            image.save(os.path.join(app.config['IMAGE_UPLOADS'],image.filename))
            mongo.save_file(image.filename,image)
            id=mongo.db.user.insert_one({'_id':ObjectId(),'username':username,'email':email,'rollno':rollno,
                                         'password':password,'mentor':mentor,'image':image.filename})
            user=mongo.db.user.find_one({'username':username,'email':email})

            print(user)
            t=json.loads(json_util.dumps(user))
            t1=t['_id']['$oid']
            t['_id']=t1
            mongo.db.mark.insert_one({'_id':ObjectId(),"total":0,"paper":0,"project":0,"club":0,
                                      "internship":0,"placement":0,"vac":0,"gate":0,"sports":0,
                                      "other":0,"ncc":0,"obtained":0,'username':username,'rollno':rollno,
                                      'creator':t['_id']})
            return {'user':[t],'message':'successfully signed up'}
    except:
        return{'user':None,'message':'Email or RollNo already Exists'}

@app.route('/user/<id>',methods=['GET','PUT'])
def givingback(id):
    if request.method=='GET':
        print(id)
        user=mongo.db.user.find_one({'_id':ObjectId(id)})
        print(user)
        t=json.loads(json_util.dumps(user))
        t1=t['_id']['$oid']
        t['_id']=t1
        imgname=t['image']
        t['image']='http://localhost:5000/images/'+imgname
        print(imgname)

        return {'user':[t],'message':'success'}
    elif request.method=='PUT':
        try:
            username= request.form["username"]
            email= request.form["email"]
            rollno= request.form["rollno"]
            password= generate_password_hash(request.form["password"])
            mentor= request.form["mentor"]
            image = request.files['image']
            image.save(os.path.join(app.config['IMAGE_UPLOADS'],image.filename))
            #mongo.save_file(image.filename,image)
            mongo.db.user.find_one_and_update({'_id':ObjectId(id)},{'$set':{'username':username,'email':email,'rollno':rollno,'password':password,'mentor':mentor,'image':image.filename}})
            user=mongo.db.user.find_one({'username':username,'email':email})
            print(user)
            t=json.loads(json_util.dumps(user))
            t1=t['_id']['$oid']
            t['_id']=t1
            return {'user':[t],'message':'success'}
        except:
            return {'user':None,'message':'Email or RollNo already Exists'}


@app.route('/activity/<id>',methods=['POST','PUT','DELETE'])
def get_activity_byid(id):
    if request.method=='PUT':
        req = request.json
        # name=req['name']
        # location=req['location']
        # mode= req['mode']
        # prize=req['prize']
        # endDate=req['endDate']
        # mark=req['mark']
        # type= req['type']
        # uploadedDate=req['uploadedDate']
        # image = request.files['image']
        # print(image)
        # f=image.filename+'.jpg'
        # req.update({'image':f})
        # image.save(os.path.join(app.config['CLIENT_IMAGES'],f))
        # # mongo.save_file(image.filename,image)
        # f1='http://localhost:5000/images/'+id+'-'+f
        #Id=mongo.db.act.find_one_and_update({'_id':ObjectId(id)},{'$set':req})
        activity=mongo.db.act.find_one({'_id':ObjectId(id)})
        t=json.loads(json_util.dumps(activity))
        t1=t['_id']['$oid']
        t['_id']=t1
        activity1=mongo.db.mark.find_one({'creator':t['creator']})
        t2=json.loads(json_util.dumps(activity1))
        print(t['mark'],req['mark'],t2[t['type']])
        tomod=t['mark']
        tomod=int(t2[t['type']])-int(tomod)
        tomod+=int(req['mark'])
        print(t2,tomod)
        mongo.db.mark.find_one_and_update({'creator':t['creator']},{'$set': {t['type']:tomod}})
        Id=mongo.db.act.find_one_and_update({'_id':ObjectId(id)},{'$set':req})
        return {'activity':t,'message':'success'}

    if request.method=='POST':
        req=request.form.to_dict()
        # name=req['name']
        # location=req['location']
        # mode= req['mode']
        # prize=req['prize']
        # endDate=req['endDate']
        # mark=req['mark']
        type= req['type']
        # uploadedDate=req['uploadedDate']
        image = request.files['image']
        print(image)
        f=image.filename+'.jpg'
        image.save(os.path.join(app.config['CLIENT_IMAGES'],f))
        # mongo.save_file(image.filename,image)
        f1='http://localhost:5000/images/'+f
        req.update({'isLocked':False,'image':f1,'creator':id})
        print('req,',req)
        Id=mongo.db.act.insert_one(req)
        #here false f can also be capital
        activity=mongo.db.act.find_one(Id.inserted_id)
        t=json.loads(json_util.dumps(activity))
        print(t)
        t1=t['_id']['$oid']
        t['_id']=t1

        activity1=mongo.db.mark.find_one({'creator':id})
        t2=json.loads(json_util.dumps(activity1))
        print(t2)
        temp=t2[t['type']]
        t2[t['type']]=temp+int(t['mark'])
        m=mongo.db.mark.find_one_and_update({'creator':id},{'$set': {t['type']:t2[t['type']]}})
        return {'activity':t,'message':'successfully added'}

    if request.method=='DELETE':
        activity=mongo.db.act.find_one({'_id':ObjectId(id)})
        t=json.loads(json_util.dumps(activity))
        print(t)
        c=t['creator']
        m=t['mark']
        type=t['type']
        mark=mongo.db.mark.find_one({'creator':c})
        todel=json.loads(json_util.dumps(mark))
        print(todel)
        temp=todel[type]
        temp-=int(m)
        mongo.db.mark.find_one_and_update({'creator':c},{'$set':{type:temp}})
        mongo.db.act.delete_one({'_id':ObjectId(id)})
        return ({'activityId':id,'message':'successfully deleted'})

@app.route('/activity/<id>',methods=['GET'])
def get_activity_byid2(id):
    if request.method=='GET':
        Id=mongo.db.act.find_one({'_id':ObjectId(id)})
        print(Id)
        t=json.loads(json_util.dumps(Id))
        t1=t['_id']['$oid']
        t['_id']=t1

        return {'activity':t,'message':'success'}


@app.route('/activity/s/<id>',methods=['GET'])
def get_activity_byid3(id):
    if request.method=='GET':
        d=[]
        try:
            for i in mongo.db.act.find({'creator':id}):
                t=mongo.db.act.find_one({'_id':i['_id']})
                t=json.loads(json_util.dumps(t))
                t1=t['_id']['$oid']
                t['_id']=t1
                d.append(t)

            # t=json.loads(json_util.dumps(Id))
            print('this',t)
            return {'activities':d,'message':'Activities Fetched Successfully!'}
        except:
            return{'activities':None,'message':'None activities'}
@app.route('/mark/<id>',methods=['GET'])
def mark(id):
    # for i in mongo.db.act.find({},{'creator':id}):
    #     t=mongo.db.act.find_one({'_id':i['_id']})
    #     t=json.loads(json_util.dumps(t))
    #     t1=t['_id']['$oid']
    #     t['_id']=t1
    #     d.append(t)
    mark=mongo.db.mark.find_one({'creator':id})
    print(mark)
    t=json.loads(json_util.dumps(mark))
    t1=t['_id']['$oid']
    t['_id']=t1
    check=["club","gate","internship","ncc","other","paper","placement","project","sports","vac"]
    tot=0
    for i in check:
        tot+=int(t[i])
    t['total']=tot
    t['obtained']=t['total']//20
    return jsonify({'mark':[t],'message':'fetched successfully'})


@app.route('/images/<path:name>',methods=['GET'])
def imagee(name):
    try:
        return send_from_directory('images',name)
    except:
        return {'message':'not found','B':False}

######################################################################################################################
@app.route('/admin/login',methods=['POST','PUT'])
def for_admin():
    req=request.get_json()
    try:
        t=mongo.db.adminn.find_one({'email':req['email']})
        t=json.loads(json_util.dumps(t))
        t1=t['_id']['$oid']
        t['_id']=t1
        # if t['password']==req['password']:
        if check_password_hash(t['password'],req['password']):
            return {'admin':[t],'message':'successfully verified'}
    except:
        return {'admin':None,'message':'Not verified'}

@app.route('/admin/signup',methods=['POST'])
def for_adminsignup():
    req=request.get_json()
    try:
        password=generate_password_hash(req['password'])
        req['password']=password
        Id=mongo.db.adminn.insert_one(req)
        ad=mongo.db.adminn.find_one(Id.inserted_id)
        t=json.loads(json_util.dumps(ad))
        t1=t['_id']['$oid']
        t['_id']=t1
        return {'admin':t,'message':'successfully verified'}
    except:
        print(req)
        return {'admin':None,'message':'Not verified'}

@app.route('/admin/<name>',methods=['GET','DELETE'])
def for_adminsget(name):
    if request.method=='GET':
        print(name)
        try:
            ad=mongo.db.adminn.find_one({'name':name})
            t=json.loads(json_util.dumps(ad))
            t1=t['_id']['$oid']
            t['_id']=t1
            return {'admin':t,'message':'successfully verified'}
        except:
            return {'admin':None,'message':'Not verified'}
    if request.method=='DELETE':
        try:
            id=mongo.db.adminn.find_one_and_delete({'_id':ObjectId(name)})
            return {'adminId':name,'message':'successfully deleted'}
        except:
            return {'adminId':None,'message':'not deleted'}

@app.route('/user/<name>/admin-name',methods=['GET'])
def for_adminget(name):
    print(name)
    d=[]
    try:
        for i in mongo.db.user.find({'mentor':name}):
                # t=mongo.db.act.find_one({'_id':i['_id']})
            t=json.loads(json_util.dumps(i))
            t1=t['_id']['$oid']
            t['_id']=t1
            d.append(t)
        return {'users':d,'message':'fetched'}
    except:
        return {'users':None,'message':'Not fetched'}

@app.route('/mark/',methods=['GET'])
def for_admingetmark():
    try:
        d=[]
        i=mongo.db.mark.find()
        # for i in mongo.db.mark.find():
        #         # t=mongo.db.act.find_one({'_id':i['_id']})
        t=json.loads(json_util.dumps(i))
        for j in t:
            t1=j['_id']['$oid']
            j['_id']=t1
            d.append(j)
        return {'marks':d,'message':'successfully verified'}
    except:
        return {'marks':None,'message':'successfully verified'}

@app.route('/admin/',methods=['GET'])
def for_admingetadminn():
    try:
        d=[]
        i=mongo.db.adminn.find()
        # for i in mongo.db.mark.find():
        #         # t=mongo.db.act.find_one({'_id':i['_id']})
        t=json.loads(json_util.dumps(i))
        for j in t:
            t1=j['_id']['$oid']
            j['_id']=t1
            d.append(j)
        return {'admins':d,'message':'fetched successfully'}
    except:
        return {'admins':None,'message':'not fetched successfully'}


if __name__=="__main__":
    app.run(debug=True)
