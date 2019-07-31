import flask
from flask import request, jsonify, json
from flask import Response
import datetime
import sqlite3
from functools import wraps
import hashlib

from cassandra.cluster import Cluster

from wsgiref.handlers import format_date_time
from time import mktime


app = flask.Flask(__name__)
app.config["DEBUG"] = True

author = ''

DATABASE = 'commentsDB.db'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# app.config['BASIC_AUTH_USERNAME'] = 'john'
# app.config['BASIC_AUTH_PASSWORD'] = 'matrix'

# basic_auth = BasicAuth(app)

# class check(BasicAuth):
#     def check_credentials(username, password):
#         return true

# def check_auth(username, password):
#     """This function is called to check if a username /
#     password combination is valid.
#     """
#     conn = sqlite3.connect('blog.db')

#     c = conn.cursor()

#     c.execute("Select password from user where name = (:username) and isDeleted=0", {"username": username})

#     pswd = c.fetchone()

#     if pswd is None:
#         return False

#     pswd = str(pswd[0])
#     db_password = hashlib.md5(password.encode())
#     db_password = str(db_password.hexdigest())    
#     # pswd = pswd[0]

#     print(pswd)
#     print(db_password)


#     if pswd is not None:
#         return pswd == db_password
    


    # return username == 'john' and password == 'matrix'

# def authenticate():
#     """Sends a 401 response that enables basic auth"""
#     # return "invalid"

#     resp = Response(status=404, mimetype='application/json')


#     return resp

# def auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         global author
#         if not auth or not check_auth(auth.username, auth.password):
#             author = 'Anonymous Coward'
#         else:
#             author= auth.username
#         return f(*args, **kwargs)
#     return decorated

# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if not auth or not check_auth(auth.username, auth.password):
#             return authenticate()
#         global author 
#         author= auth.username
#         return f(*args, **kwargs)
#     return decorated


@app.route('/', methods=['GET'])
def home():
    return "<h1>Comments API</p>"

@app.route('/new', methods=['POST'])
# @auth
def new():

    result = request.json

    if 'comment' in result:
        comment = result['comment']
    else:
        return "Error: No comment field provided. Please specify comment."

    if 'title' in result:
        title = result['title']
    else:
        return "Error: No title field provided. Please specify an title."

    # if 'author' in result:
    #     author = result['author']
    # else:
    #     return "Error: No author field provided. Please specify an author."
    global author

    author = request.authorization.username

    # connection

    try:

        # conn = sqlite3.connect('blog.db')
        # connArticle = sqlite3.connect('articleDB.db')

        # c = connArticle.cursor()
        cluster = Cluster(['172.17.0.2'])
        session = cluster.connect('blog')

        curDate = datetime.datetime.now()
        stamp = mktime(curDate.timetuple())
        curDate = format_date_time(stamp)

        

        rows= session.execute("""select Id from blogdata where isDeleted = 0 and title = %(title)s ALLOW FILTERING""", {'title': title})

        # result_set = c.fetchone()

        # connArticle.close()

        id = None

        for row in rows:
            id = row.id

        print(id)

        if id is None:
            # conn.close()
            resp = Response(status=404, mimetype='application/json')
            # return "Article doesn't exist or may have been deleted"
            return resp

        

        # connComments = sqlite3.connect('commentsDB.db')
        # c = connComments.cursor()

        # for row in result_set:
        #     id = row["articleId"]

        rows = session.execute("""Select max(Id) as id from blogData;""")

        for row in rows:
            newid = row.id

        if newid is None:
            newid = 1
        else:
            newid = newid + 1 

        print(newid)
            
        

        session.execute("""insert into blogdata (Title, comment, author, createdDate, isDeleted, datatype, id) 
         values(%(title)s,%(comment)s,%(author)s,%(date)s,0,'C',%(id)s);""",
         {'title': title, 'comment': comment, 'author': author, 'date': str(curDate), 'id': newid })
        
        # connComments.commit()

        # c.execute("select * from comments where isDeleted= 0")

        # print(c.fetchall())

        # connComments.close()

        resp = Response(status=201, mimetype='application/json')

    except sqlite3.Error as e:

        resp = Response(status=409, mimetype='application/json')

    # resp = Response(js, status=200, mimetype='application/json')
    # resp.headers['Link'] = 'http://'

    # return "Comment Created"
    return resp

    
@app.route('/delete', methods=['DELETE'])
# @requires_auth
def delete():


    # if 'id' in request.args:
    #     id = request.args['id']
    # else:
    #     return "Error: No id field provided. Please specify id of the article."

    # connection

    result = request.json

    author = request.authorization.username

    if 'id' in result:
        id = result['id']
    else:
        return "Error: No ID field provided. Please specify ID."

    try:


        cluster = Cluster(['172.17.0.2'])
        session = cluster.connect('blog')

        rows = session.execute(""" select id from blogdata
                        where id= %(id)s and isdeleted= 0 and datatype = 'C' and Author=%(author)s ALLOW FILTERING""",
                        {'id': id, 'author': author})

        id = None

        for row in rows:
            id = row.id

        if id is None:
            resp = Response(status=404, mimetype='application/json')
            return resp


        session.execute("""update blogdata
            set isDeleted = 1
            where Id = %(id)s and datatype='C'""",
             {'id': id,})


        # connComments.commit()

        # c.execute("select * from comments where isDeleted= 0")

        # print(c.fetchall())

        # connComments.close()

        resp = Response(status=200, mimetype='application/json')

    except sqlite3.Error as e:

        resp = Response(status=409, mimetype='application/json')

    return resp

@app.route('/count/<title>', methods=['GET'])
def count(title):

    if title == '':
        return "Error: No title field provided. Please specify title of the article."

    # connection

    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect('blog')

    

    rows=session.execute("""select id from blogdata where isDeleted = 0 and Title = %(title)s and datatype= 'A' Allow filtering""",
     {'title': title})

    id = None

    for row in rows:
        id = row.id

    if id is None:
        # connComments.close()
        resp = Response(status=404, mimetype='application/json')
        # return "Article doesn't exist or may have been deleted"
        return resp
        # return "Number of comments for given article: 0"

    result = session.execute("select max(createddate) as last from blogdata where isDeleted = 0 and dataType = 'C' and title= %(title)s Allow Filtering", {'title': title})

    max  = None
    for row in result:
        max = row.last

    if result is None:
        resp = Response(status=404, mimetype='application/json')
        return resp

    ifModifiedSince= request.headers.get('If-Modified-Since')

    # return ifModifiedSince

    if ifModifiedSince is not None:
        if str(ifModifiedSince) >= str(max):
            resp = Response(status=304, mimetype='application/json')
            return resp

    rows = session.execute("""
        select count(id) as count from blogdata
        where Title= %(title)s and isDeleted = 0 and datatype='C' Allow filtering""",
         {"title":title})

    # commentsCount = c.fetchone()
    # commentsCount = str(commentsCount[0])

    for row in rows:
        count = row.count

    # connComments.close()

    resp = jsonify("Number of comments for given article:" + str(count))
    resp.headers['last-modified']= max
    resp.headers['Cache-Control'] = 'public, max-age=300'

    return resp

    # return "Number of comments for given article:" + str(count)

@app.route('/retrieve/<title>/<num>', methods=['GET'])
def retrieve(title, num):

    # if 'number' in request.args:
    #     num = request.args['number']
    # else:
    #     num = -1

    # if 'title' in request.args:
    #     title = request.args['title']
    # else:
    #     return "Error: No title field provided. Please specify title of the article."


    # connection

    # connComments = sqlite3.connect('commentsDB.db')
    
    # c = connComments.cursor()
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect('blog')

    rows = session.execute("""select id from blogdata where isDeleted = 0 and Title = %(title)s and datatype='A' Allow filtering""",
         {'title': title})

    id = None

    for row in rows:
        id = row.id

    if id is None:
        # connComments.close()
        resp = Response(status=404, mimetype='application/json')
        return resp
        # return "Article doesn't exist or may have been deleted"

    result = session.execute("select max(createddate) as last from blogdata where isDeleted = 0 and dataType = 'C' and title= %(title)s Allow Filtering", {'title': title})

    max  = None
    for row in result:
        max = row.last

    if result is None:
        resp = Response(status=404, mimetype='application/json')
        return resp

    ifModifiedSince= request.headers.get('If-Modified-Since')

    # return ifModifiedSince

    if ifModifiedSince is not None:
        if str(ifModifiedSince) >= str(max):
            resp = Response(status=304, mimetype='application/json')
            return resp

    # connComments.row_factory = dict_factory
    # c = connComments.cursor()

    result=session.execute("""
            
            SELECT comment FROM blogdata where isDeleted = 0 and Title = %(title)s and datatype='C' LIMIT %(number)s Allow filtering
            ;""", {'number': int(num), "title":title})

    # result = jsonify(c.fetchall())

    # connComments.close()

    resp = jsonify(list(result))
    resp.headers['last-modified']= max
    resp.headers['Cache-Control'] = 'public, max-age=300'

    return resp

    # return jsonify(list(result))

app.run()

