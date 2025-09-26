from flask import Flask,request,jsonify,send_from_directory
from flask_cors import CORS
import util
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

from auth import init_auth 
load_dotenv()
app=Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
init_auth(app)  
util.load_saved_artifacts() 

@app.route('/<path:filename>')
def serve_client_files(filename):
    return send_from_directory('../Client', filename)

@app.route('/')
def home():
    return send_from_directory('../Client', 'index.html')


@app.route('/pestIdentifier')
def pest_identifier():
    return send_from_directory('../Client', 'pest_detector.html')

@app.route('/detectPest', methods=['GET','POST'])
def predict_pest():

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    
    #  Save file temporarily
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    # Get predictions
    predictions = util.get_prediction(file_path)

    return jsonify(predictions)



@app.route('/impactAnalyzer')
def impactAnalyzer():
    return send_from_directory('../client', 'Impact_analyzer.html')


@app.route('/analyzeImpact', methods=['POST'])
def Analyze():
    data=request.json
    pest=data.get("pest")
    crop=data.get("crop")

    if not pest or not crop:
        return jsonify({"error": "Both 'pest' and 'crop' must be provided"}), 400
    
    result=util.analyze(pest,crop)
    return jsonify({"Impact analysis": result})
    
@app.route('/login')
def serve_login():
    return send_from_directory('static', 'login.html')

@app.route('/register')
def serve_register():
    return send_from_directory('static', 'register.html')





if __name__=='__main__':
    app.run(debug=True)