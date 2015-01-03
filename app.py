from flask import Flask, request, redirect, url_for, make_response
from werkzeug import secure_filename
from pymongo import Connection
from bson.objectid import ObjectId
import gridfs
from werkzeug import Response


#ALLOWED_EXTENSIONS = set(['pcap', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav']) # yet to add the filters ;)

app = Flask(__name__)

def mongo_conn():
  db = Connection().myfiles
  grid = gridfs.GridFS(db)
  return grid

@app.route('/upload/', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
	filename = secure_filename(file.filename)
	print filename
	print file
	grid = mongo_conn()
	print grid
	oid = grid.put(file,content_type=file.content_type,filename="%s" %filename)
	if oid:
	  return "File succesfuly uploaded, refid: %s" %oid
	else:
	  return HTTPError(500, "Unable to upload the file")

@app.route('/search/oid/<oid>', methods=['POST','GET'])
def get_files_by_oid(oid):
    if request.method == 'GET':
        mongo_oid = oid
	grid = mongo_conn()
	try:
	  file = grid.get(ObjectId(mongo_oid))
	  print file
          return Response(file, mimetype=file.content_type, direct_passthrough=True)
	except Exception:
#        except NoFile:
          return HTTPError(404, "Not found:")

@app.route('/search/file/<filename>', methods=['POST','GET'])
def get_files_by_filename(filename):
    if request.method == 'GET':
        mongo_filename = filename
        grid = mongo_conn()
        try:
	  print "file -> %s" %mongo_filename
          file = grid.find({"filename": "%s" %mongo_filename}).sort('uploadDate', -1).limit(1)[0]
          return Response(file, mimetype=file.content_type, direct_passthrough=True)
        except NoFile:
          return HTTPError(404, "Not found:" + mongo_filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
