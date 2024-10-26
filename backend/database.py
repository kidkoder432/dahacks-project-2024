# Import required libraries and modules
from flask import Flask, request, jsonify  # Flask for API creation, request and jsonify for handling data and responses
from flask_cors import CORS  # CORS to allow cross-origin requests
from skyfield.api import load, N, W, wgs84, Star, Angle  # Skyfield for astronomical calculations
import pandas as pd  # Pandas for data handling
from random import choice  # For selecting random visible constellations
import dateutil  # For parsing timestamps
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy for ORM
from werkzeug.security import generate_password_hash, check_password_hash  # Password hashing
import jwt  # JSON Web Token for authentication
from datetime import datetime, timedelta  # For managing dates and times
from functools import wraps  # To create decorator for token authentication

# Initialize the Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Configure the app
app.config['SECRET_KEY'] = 'secret key here'  # Secret key for JWT encoding - env prob
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/spitonthatthang' - ignore this
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/constellation_db'  # Database URL - env as well prob
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications to save resources

# Initialize the SQLAlchemy object for ORM
db = SQLAlchemy(app)

# Define the User model for database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(80), unique=True, nullable=False)  # Username field
    password = db.Column(db.String(120), nullable=False)  # Password field (hashed)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Account creation timestamp
    observations = db.relationship('Observation', backref='user', lazy=True)  # Relationship with Observation model

# Define the Observation model for database
class Observation(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User table
    constellation = db.Column(db.String(80), nullable=False)  # Observed constellation name
    latitude = db.Column(db.Float, nullable=False)  # Observation latitude
    longitude = db.Column(db.Float, nullable=False)  # Observation longitude
    timestamp = db.Column(db.DateTime, nullable=False)  # Observation timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Record creation timestamp

# Token Required Decorator for protected routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Retrieve token from Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:  # If no token provided, return error
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Get user from decoded token
            current_user = User.query.get(data['user_id'])
        except:
            # Return error if token is invalid
            return jsonify({'message': 'Token is invalid'}), 401
        
        # Call the actual route function with the current user
        return f(current_user, *args, **kwargs)
    return decorated

# Registration route
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()  # Retrieve JSON data
    
    # Validate input data
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    # Hash the password and create a new user
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    
    try:
        db.session.add(new_user)  # Add user to database
        db.session.commit()  # Commit changes
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error creating user', 'error': str(e)}), 500

# Login route
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()  # Retrieve JSON data
    
    # Validate input data
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    user = User.query.filter_by(username=data['username']).first()  # Find user by username
    
    # Check password validity
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    # Generate JWT token with 1-day expiration
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, app.config['SECRET_KEY'])
    
    return jsonify({'token': token})  # Return token

# Load star data
stars = pd.read_csv("stars.csv")  # Load stars from CSV file

# Helper function to get Star object for Skyfield calculations
def get_star(ra, dec):
    return Star(ra=Angle(degrees=ra), dec=Angle(degrees=dec))

# Protected route for receiving user location
@app.route("/location", methods=["POST"])
@token_required
def receive_location(current_user):
    data = request.get_json()  # Retrieve JSON data
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

# Protected route for receiving visible constellations
@app.route("/visible", methods=["POST"])
@token_required
def receive_visible(current_user):
    data = request.get_json()  # Retrieve JSON data
    lat = data.get("latitude")
    lng = data.get("longitude")
    timestamp = data.get("timestamp")

    ts = load.timescale().utc(dateutil.parser.parse(timestamp))  # Parse timestamp
    loc = wgs84.latlon(lat * N, lng * W)  # Create location object

    visibleConstellations = []
    print(f"Received coordinates: Latitude={lat}, Longitude={lng}, Time={timestamp}")

    # Check visibility of each star in the CSV
    for star in stars.iterrows():
        star = star[1]
        starPos = loc.at(ts).observe(get_star(star["ra_degrees"], star["dec_degrees"]))  # Calculate star position
        alt, az, d = starPos.apparent().altaz()  # Get altitude and azimuth

        # If altitude is above 45 degrees, add constellation to visible list
        if alt.degrees > 45 and star["constellation"] not in visibleConstellations:
            visibleConstellations.append(star["constellation"])

    # Select a random constellation and find its brightest star
    c = choice(visibleConstellations)
    guideStar = stars[stars["constellation"] == c].loc[stars["magnitude"].idxmin()]
    starPos = loc.at(ts).observe(get_star(guideStar["ra_degrees"], guideStar["dec_degrees"]))
    alt, az, d = starPos.apparent().altaz()

    # Save the observation to the database
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

# Route to retrieve user's observation history
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

# Run the app
if __name__ == "__main__":
    # Create all database tables
    with app.app_context():
        db.create_all()
    
    # Load star data and run the app
    stars = pd.read_csv("stars.csv")
    app.run(debug=True)
