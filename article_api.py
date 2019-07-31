import flask
from flask import request, jsonify, json, Response, g, make_response
import datetime
import sqlite3
from functools import wraps
#from flask_basicauth import BasicAuth
import hashlib
from wsgiref.handlers import format_date_time
from time import mktime
from feedgen.feed import FeedGenerator
import requests
from rfeed import *

from cassandra.cluster import Cluster


# DATABASE = 'blog.db'
DATABASE = 'articleDB.db'

app = flask.Flask(__name__)
app.config["DEBUG"] = True

author = ''

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

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


@app.route('/home', methods=['GET'])
# @basic_auth.required
def home():
    return "<h1> ******Article TEST API******* </h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"
    

    # r = requests.get('http://localhost/article/retrieve/1')
    # r.status_code
    # r.headers['content-type']
    # r.encoding
    # r.text
    # return r.text 

    # fg = FeedGenerator()
    # fg.id('http://lernfunk.de/media/654321')
    # fg.title('Some Testfeed')
    # fg.author( {'name':'John Doe','email':'john@example.de'} )
    # fg.link( href='http://example.com', rel='alternate' )
    # fg.logo('http://ex.com/logo.jpg')
    # fg.subtitle('This is a cool feed!')
    # fg.link( href='http://larskiesow.de/test.atom', rel='self' )
    # fg.contributor([{'name':'John Doe', 'email':'jdoe@example.com'},{'name':'John Doe', 'email':'jdoe@example.com'},{'name':'John Doe', 'email':'jdoe@example.com'}])
    # fg.language('en')

    # rssfeed  = fg.rss_str(pretty=True)

    # return rssfeed

    # blog1 = json.loads(r.text)
    # blog1 = blog1[0]
    # r = Blog(
    #     content = blog1["content"]
    # )

    # item1 = Item(
    # title = "First article",
    # link = "http://www.example.com/articles/1", 
    # description = "This is the description of the first article",
    # author = "Santiago L. Valdarrama",
    # guid = Guid("http://www.example.com/articles/1"),
    # pubDate = datetime.datetime(2014, 12, 29, 10, 00))

    # item2 = Item(
    # title = "Second article",
    # link = "http://www.example.com/articles/2", 
    # description = "This is the description of the second article",
    # author = "Ratik L. Valdarrama",
    # guid = Guid("http://www.example.com/articles/2"),
    # pubDate = datetime.datetime(2014, 12, 30, 14, 15))

    # feed = Feed(
    # title = "Sample RSS Feed",
    # link = "http://www.example.com/rss",
    # description = "This is an example of how to use rfeed to generate an RSS 2.0 feed",
    # language = "en-US",
    # lastBuildDate = datetime.datetime.now(),
    # # items = [item1, item2],
    # blogs = [r])

    # return (feed.rss())


@app.route('/new', methods=['POST'])
#@requires_auth
def new():


    result = request.json

    if 'content' in result:
        content = result['content']
    else:
        return "Error: No content field provided. Please specify an content."

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

    

    curDate = datetime.datetime.now()
    stamp = mktime(curDate.timetuple())
    curDate = format_date_time(stamp)

    try:
        # conn = sqlite3.connect('blog.db')
        # conn = sqlite3.connect('articleDB.db')
        cluster = Cluster(['172.17.0.2'])
        session = cluster.connect('blog')

        temp_title = title.replace(" ","%20")

        print(temp_title)

        rows = session.execute("""Select max(Id) as id from blogData;""")

        for row in rows:
            id = row.id

        if id is None:
            id = 1
        else:
            id = id + 1 

        # c = conn.cursor()


        session.execute("""insert into blogData (content, title, Author, url, createdDate, modifiedDate, isDeleted, dataType, Id) 
        values (%(content)s, %(title)s, %(author)s, %(url)s, %(createdDate)s, %(modifiedDate)s, 0, 'A', %(id)s)""",
         {'content': content, 'title': title, 'author': author, 'createdDate': str(curDate), 'modifiedDate': str(curDate), 'url': 'http://localhost/article/search/' + temp_title, 'id':id})
        
        # conn.commit()

        # c.execute("select * from article where isDeleted= 0")

        # print(title)

        # conn.close()

        resp = Response(status=201, mimetype='application/json')
        resp.headers['location'] = 'http://localhost/article/search/' + title

        # response = jsonify()
        # response.status_code = 201
        # response.headers['location'] = 'http://127.0.0.1:5000/search?title='
        # response.autocorrect_location_header = False
        # return response
        
    except sqlite3.Error as e:
        resp = Response(status=409, mimetype='application/json')

    return resp


@app.route('/search/<title>', methods=['GET'])
def search(title):

    # if 'title' in request.args:
    #     title = request.args['title']
    # else:
    #     return "Error: No title field provided. Please specify Title of the article."

    if title =='':
        return "Error: No title field provided. Please specify Title of the article."

    # connection

    # conn = sqlite3.connect('blog.db')
    # conn = sqlite3.connect('articleDB.db')
    # conn.row_factory = dict_factory
    # c = conn.cursor()

    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect('blog')

    # db = get_db()
    
    #c = db.cursor()

    result = session.execute("select max(modifiedDate) as last from blogdata where isDeleted = 0 and dataType = 'A' and title = %(title)s Allow Filtering", {'title': title})

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

    

    result = session.execute("select content from blogData where isDeleted = 0 and title = %(title)s and dataType='A' ALLOW FILTERING", {'title': title})

    # result = c.fetchone()

    # print(jsonify(list(result)))

    if result is None:
        resp = Response(status=404, mimetype='application/json')
        return resp

    # data = jsonify(list(result))

    # resp = Response(data, status=200, mimetype='application/json')

    # c.close()]
    # resp = Response(status=200, mimetype='application/json')
    resp = jsonify(list(result))
    resp.headers['last-modified']= max

    return resp
    # return jsonify(list(result))

@app.route('/edit', methods=['PATCH'])
#@requires_auth
def edit():

    result = request.json

    if 'title' in result:
        title = result['title']
    else:
        return "Error: No title field provided. Please specify an title."

    if 'content' in result:
        content = result['content']
    else:
        return "Error: No content field provided. Please specify an content."

    global author

    author = request.authorization.username


    # connection

    # conn = sqlite3.connect('blog.db')
    # conn = sqlite3.connect('articleDB.db')

    # c = conn.cursor()
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect('blog')

    curDate = datetime.datetime.now()
    stamp = mktime(curDate.timetuple())
    curDate = format_date_time(stamp)

    rows = session.execute("""Select id from blogData where title = %(title)s ALLOW FILTERING;""",{'title':title})

    id = None
    for row in rows:
        id = row.id

    if id is None:
        return 'Not found'

    session.execute("""UPDATE blogData
            set content = %(content)s,
            ModifiedDate = %(date)s,
            Author = %(author)s
            where Id = %(id)s and datatype='A'""",
             {'content': content, 'title': title, 'date': str(curDate), "author": author, 'id':id})

    # conn.commit()

    # conn.close()

    resp = Response(status=200, mimetype='application/json')
    return resp

    # return "Article updated"


@app.route('/delete/<title>', methods=['DELETE'])
#@requires_auth
def delete(title):

    # if 'title' in request.args:
    #     title = request.args['title']
    # else:
    if title == '':
        return "Error: No title field provided. Please specify Title of the article."

    global author

    author = request.authorization.username

    # connection

    # conn = sqlite3.connect('blog.db')
    # conn = sqlite3.connect('articleDB.db')

    # c = conn.cursor()
    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect('blog')

    rows = session.execute("""select *
                            from blogData
                            where isDeleted = 0 and Author= %(author)s and title = %(title)s and dataType='A' ALLOW FILTERING""",
         {'title': title, 'author': author})

    title = None
    id = None

    for row in rows:
        title = row.title
        id = row.id
        

    if title is None:
        return "Error: No test"


    session.execute("""update blogData
        set isDeleted = 1
        where datatype='A' and Id= %(id)s """,
         {'title': title, 'id':id})

   


    # conn.commit()
    # conn.close()

    resp = Response(status=200, mimetype='application/json')
    return resp

    # return "Article Deleted"

@app.route('/retrieve/<num>', methods=['GET'])
def retrieve(num):

    # if 'number' in request.args:
    #     num = request.args['number']
    # else:
        # num = -1

    # connection

    # conn = sqlite3.connect('blog.db')
    # conn = sqlite3.connect('articleDB.db')
    # conn.row_factory = dict_factory
    # c = conn.cursor()

    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect('blog')

    result = session.execute("select max(modifiedDate) as last from blogdata where isDeleted = 0 and dataType = 'A' Allow Filtering")

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

    

    if num is -1:
        print('')

        # c.execute("SELECT content FROM article where isDeleted = 0 ORDER BY articleId DESC")

    else:
        rows = session.execute("""SELECT content FROM blogdata where isdeleted=0 and datatype='A' LIMIT %(number)s Allow Filtering;""",
             {'number': int(num)})

    # result = jsonify(c.fetchall())

    # conn.close()

    resp = jsonify(list(rows))
    resp.headers['last-modified']= max

    return resp

    # return jsonify(list(rows)) 

@app.route('/meta/<num>', methods=['GET'])
def meta(num):

    # if 'number' in request.args:
    #     num = request.args['number']
    # else:
    #     num = -1

    # connection

    # conn = sqlite3.connect('blog.db')
    # conn = sqlite3.connect('articleDB.db')
    # conn.row_factory = dict_factory
    # c = conn.cursor()

    cluster = Cluster(['172.17.0.2'])
    session = cluster.connect('blog')

    result = session.execute("select max(modifiedDate) as last from blogdata where isDeleted = 0 and dataType = 'A' Allow Filtering")

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


    if num is -1:

        # c.execute("SELECT * FROM article where isDeleted = 0 ORDER BY articleId DESC")
        print('')
    else:
        result = session.execute("""
             
            SELECT * FROM blogdata where isDeleted = 0 and datatype='A' LIMIT %(number)s ALLOW FILTERING
            ;""", {'number': int(num)})

    # result = jsonify(c.fetchall())

    # conn.close()

    resp = jsonify(list(result))
    resp.headers['last-modified']= max
    resp.headers['Cache-Control'] = 'public, max-age=300'

    return resp

    # return jsonify(list(result)) 

app.run()