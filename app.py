from flask import Flask, request, redirect, url_for, make_response, jsonify
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
	grid = mongo_conn()
	oid = grid.put(file,content_type=file.content_type,filename="%s" %filename)
	if oid:
 	  response = jsonify(result={"status": 201, "description": "File succesfuly uploaded, RefID: %s" %oid})
	  response.status_code = 201
	  return response
	else:
	  response = jsonify(result={"status": 500, "description": "UH OH Something Went Wrong :("})
	  response.status_code = 500
	  return response

@app.route('/search/oid/<oid>', methods=['POST','GET'])
def get_files_by_oid(oid):
    if request.method == 'GET':
        mongo_oid = oid
	grid = mongo_conn()
	try:
	  file = grid.get(ObjectId(mongo_oid))
          return Response(file, mimetype=file.content_type, direct_passthrough=True)
	except Exception, e:
          response = jsonify(result={"status": 404, "description": "UH OH File not Found :("})
          response.status_code = 404
          return response

@app.route('/search/file/<filename>', methods=['POST','GET'])
def get_files_by_filename(filename):
    if request.method == 'GET':
        mongo_filename = filename
        grid = mongo_conn()
        try:
          file = grid.find({"filename": "%s" %mongo_filename}).sort('uploadDate', -1).limit(1)[0]
          return Response(file, mimetype=file.content_type, direct_passthrough=True)
	except Exception, e:
	  response = jsonify(result={"status": 404, "description": "UH OH File not Found :("})
	  response.status_code = 404
	  return response


@app.route('/file/oid/<oid>', methods=['DELETE'])
def del_files_by_oid(oid):
    if request.method == 'DELETE':
        mongo_oid = oid
        grid = mongo_conn()
        try:
          file = grid.delete(ObjectId(mongo_oid))
	  response = jsonify(result={"status": 200, "description": "File successfully deleted"})
	  response.status_code = 200
	  return response
        except Exception, e:
          response = jsonify(result={"status": 404, "description": "UH OH File not Found :("})
          response.status_code = 404
          return response

if __name__ == "__main__":
    app.run(host='0.0.0.0')
