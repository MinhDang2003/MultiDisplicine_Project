from flask import Flask , jsonify, request , make_response

from flask_jwt_extended import jwt_required , JWTManager

from flask_cors import CORS, cross_origin


from datetime import  timedelta 

 
from presenter import Presenter
import uuid

app = Flask(__name__)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# app.config['SESSION_USE_SIGNER'] = True
# app.config['SESSION_REDIS'] = redis.from_url("redis://127.0.0.1:6379")
# server_session = Session(app)
#app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=30000)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=48000000)
app.config['SESSION_COOKIE_HTTPONLY'] = True
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)



app.config["JWT_SECRET_KEY"] = b"6hc/_gsh,./;2ZZx3c6_s,1//"

jwt = JWTManager(app)

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

@app.route('/users/refresh',methods=['GET'])
@jwt_required(optional=True,verify_type=True)
def refresh_expiring_jwts():    
    return Presenter.handleRefresh()

@app.route('/users/signin',methods=['POST'])
def signin():
    return Presenter.handleSignIn()

@app.route('/users/signup',methods=['POST'])
def signup():
    return Presenter.handleSignUp()

@app.route("/users/checkEmail",methods=['POST'])
def checkEmailAvailable():
    return Presenter.handleCheckEmail()
    
@app.route("/users/logout", methods=["POST"])
def logout():
    return Presenter.handleLogOut()
    
@app.route('/users/profile',methods = ["GET"])
@jwt_required()
def my_profile():
    return Presenter.handleProfile()

@app.route("/api/temperature",methods=['POST'])
def temperature():
    return Presenter.handle_get_temp()

@app.route("/api/humidity",methods=['POST'])
def humidity():
    return Presenter.handle_get_humid()

@app.route("/api/brightness",methods=['POST'])
def brightness():
    return Presenter.handle_get_brightness()

@app.route("/api/current_temperature",methods=['POST'])
def current_temperature():
    return Presenter.handle_get_current_temp()

@app.route("/api/current_humidity",methods=['POST'])
def current_humidity():
    return Presenter.handle_get_current_humid()

@app.route("/api/current_brightness",methods=['POST'])
def current_brightness():
    return Presenter.handle_get_current_brightness()
#######################################
@app.route("/api/new_app",methods=['POST'])
def new_appliance():
    return Presenter.addAppliances()

@app.route("/api/del_app",methods=['POST'])
def delete_appliance():
    return Presenter.deleteAppliances()

@app.route("/api/new_room",methods=['POST'])
def new_room():
    return Presenter.createNewRoom()

@app.route("/api/del_room",methods=['POST'])
def delete_room():
    return Presenter.deleteRoom()

@app.route("/api/fan",methods=['POST'])
def fan():
    return Presenter.handle_update_fan()

@app.route("/api/light",methods=['POST'])
def light():
    return Presenter.handle_update_light()

@app.route("/api/getAllRoom",methods=['GET'])
def getAllRoom():
    return Presenter.getAllRoom()

@app.route("/api/getRoom",methods=['POST'])
def getRoom():
    return Presenter.getRoom()

@app.route("/api/getFeedList",methods= ['POST'])
def getFeedList():
    return Presenter.getFeedList()

@app.route("/api/getTrainImgs",methods= ['POST'])
@jwt_required()
def uploadImg():
    if request.method == 'OPTIONS':
        print("Fake")
        # This is the preflight request. 
        # You can do your custom handling here. 
        return _build_cors_preflight_response()
    print("Real")
    return Presenter.getImgs()

@app.route("/api/verification",methods=['POST'])
@jwt_required()
def verify():
    return Presenter.verify()
if __name__ == "__main__":
    app.run(debug=True,port=8090)
    
    