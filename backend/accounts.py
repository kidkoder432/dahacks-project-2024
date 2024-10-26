from flask import Flask, request, jsonify
from flask_cors import CORS
from skyfield.api import load, N, W, wgs84, Star, Angle
import pandas as pd
from random import choice
import dateutil
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'secret key here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/constellation_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable = False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    observations = db.relationship('Observation', backref='user', lazy=True)

class Observation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    constellation = db.Column(db.String(80), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Token Required Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Authentication Routes
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error creating user', 'error': str(e)}), 500
    
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, app.config['SECRET_KEY'])
    
    return jsonify({'token': token})

# Load star data
stars = pd.read_csv("stars.csv")

# Existing helper functions
def get_star(ra, dec):
    return Star(ra=Angle(degrees=ra), dec=Angle(degrees=dec))

# Protected routes that require authentication
@app.route("/location", methods=["POST"])
@token_required
def receive_location(current_user):
    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    timestamp = data.get("timestamp")
    
    print(f"Received coordinates: Latitude={latitude}, Longitude={longitude}, Time={timestamp}")
    
    return jsonify({
        "message": "Location and time received",
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp,
    })

@app.route("/visible", methods=["POST"])
@token_required
def receive_visible(current_user):
    data = request.get_json()
    lat = data.get("latitude")
    lng = data.get("longitude")
    timestamp = data.get("timestamp")

    ts = load.timescale().utc(dateutil.parser.parse(timestamp))
    loc = wgs84.latlon(lat * N, lng * W)

    visibleConstellations = []
    print(f"Received coordinates: Latitude={lat}, Longitude={lng}, Time={timestamp}")

    for star in stars.iterrows():
        star = star[1]
        starPos = loc.at(ts).observe(get_star(star["ra_degrees"], star["dec_degrees"]))
        alt, az, d = starPos.apparent().altaz()

        if alt.degrees > 45 and star["constellation"] not in visibleConstellations:
            visibleConstellations.append(star["constellation"])

    c = choice(visibleConstellations)
    guideStar = stars[stars["constellation"] == c].loc[stars["magnitude"].idxmin()]
    starPos = loc.at(ts).observe(get_star(guideStar["ra_degrees"], guideStar["dec_degrees"]))
    alt, az, d = starPos.apparent().altaz()

    # Save the observation
    observation = Observation(
        user_id=current_user.id,
        constellation=c,
        latitude=lat,
        longitude=lng,
        timestamp=dateutil.parser.parse(timestamp)
    )
    db.session.add(observation)
    db.session.commit()

    return jsonify({
        "message": "Visible constellations",
        "constellation": c,
        "magnitude": guideStar["magnitude"],
        "alt": alt.degrees,
        "az": az.degrees,
        "timestamp": timestamp,
    })

# Route to get user's observation history
@app.route("/observations", methods=["GET"])
@token_required
def get_observations(current_user):
    observations = Observation.query.filter_by(user_id=current_user.id).order_by(Observation.created_at.desc()).all()
    return jsonify({
        'observations': [{
            'constellation': obs.constellation,
            'latitude': obs.latitude,
            'longitude': obs.longitude,
            'timestamp': obs.timestamp.isoformat(),
            'created_at': obs.created_at.isoformat()
        } for obs in observations]
    })

if __name__ == "__main__":
    # Create all database tables
    with app.app_context():
        db.create_all()
    
    # Load star data and run the app
    stars = pd.read_csv("stars.csv")
    app.run(debug=True)