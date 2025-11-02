from flask import Flask
from flask_cors import CORS
import os

from flask_jwt_extended import JWTManager
from models import db
from routes import jobs_bp, auth_bp, applications_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

CORS(app, origins=['http://localhost:5173', 'http://localhost:3000'], supports_credentials=True, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
jwt = JWTManager(app)
db.init_app(app)

app.register_blueprint(jobs_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(applications_bp, url_prefix='/api')

@app.route('/')
def index():
    return {'message': 'WorkBridge API is running'}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
