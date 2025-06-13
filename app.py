from http import client
from flask import Flask, Response, render_template, request, jsonify, session, redirect, url_for, current_app
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
import requests
from flask import flash 
from flask_login import LoginManager, current_user, UserMixin, login_user, logout_user, login_required

# from google.cloud import texttospeech

# lient = texttospeech.TextToSpeechClient()

# Function to convert text to speech
# def text_to_speech(text, language_code='en-US', voice_name='en-US-Wavenet-F'):
#     synthesis_input = texttospeech.SynthesisInput(text=text)
#     voice = texttospeech.VoiceSelectionParams(
#         language_code=language_code,
#         name=voice_name
#     )
#     audio_config = texttospeech.AudioConfig(
#         audio_encoding=texttospeech.AudioEncoding.MP3
#     )
#     response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
#     return response.audio_content



app = Flask(__name__)
babel = Babel(app)


LANGUAGES = ['en', 'fr']
app.config['LANGUAGES'] = LANGUAGES

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy(app)
login_manager = LoginManager(app)  

login_manager.login_view = 'signin_page' 
login_manager.login_message_category = 'info'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    gender = db.Column(db.String(10)) 
    age = db.Column(db.Integer)  
    marital_status = db.Column(db.String(20)) 
    citizenship = db.Column(db.String(100))

    
# # Example route to demonstrate text-to-speech
# @app.route('/text_to_speech', methods=['POST'])
# def text_to_speech_route():
#     if request.method == 'POST':
#         text = request.form['text']
#         language_code = request.form.get('language_code', 'en-US')
#         voice_name = request.form.get('voice_name', 'en-US-Wavenet-F')

#         audio_content = text_to_speech(text, language_code, voice_name)

#         # Return the audio file to be played
#         return Response(audio_content, mimetype='audio/mpeg')

#     return 'Method not allowed', 405

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@babel.localeselector
def get_locale():
    
    return session.get('language', 'en')

# --------------------------------------------------------------------------------
  
@app.route('/')
def indi():
    return render_template('welcome.html')

# --------------------------------------------------------------------------------

@app.route('/crop_recommendations')
def crop_recommendations():
   
    crop_recommendations = [
        {'city': 'City1', 'best_crop': 'Wheat'},
        {'city': 'City2', 'best_crop': 'Rice'},
        {'city': 'City3', 'best_crop': 'Corn'},
        
    ]
    return render_template('crop_recommendations.html', crop_recommendations=crop_recommendations)

# --------------------------------------------------------------------------------

@app.route('/signin', methods=['GET', 'POST'])
def signin_page():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

       
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user and user.password == password:
           
            login_user(user)
            return redirect(url_for('profile_page'))  
        else:
           
            flash('Invalid username or email or password. Please try again.', 'error')

    return render_template('signin.html')

# --------------------------------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        location = request.form['location']
        phone_number = request.form['phone_number']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        gender = request.form['gender']
        age = request.form['age'] 
        marital_status = request.form['marital_status']  
        citizenship = request.form['citizenship'] 

        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            
            flash('Username or email already exists. Please choose another one.', 'error')
            return redirect(url_for('register_page'))

        
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            location=location,
            phone_number=phone_number,
            username=username,
            email=email,
            password=password,
            gender=gender,
            age=age,  
            marital_status=marital_status,  
            citizenship=citizenship  
        )

       
        with app.app_context():  
            db.session.add(new_user)
            db.session.commit()

        
        user_name = f'{first_name} {last_name}'

       
        flash(Markup(f'Successfully registered! Now you can <a href="{url_for("signin_page")}">sign in</a>.'), 'success')

       

    return render_template('register.html')

# ---------------------------------------------------------------------------------------------------

@app.route('/soil_profile')
def soil_profile():
    return render_template('soil_profile.html')

# ---------------------------------------------------------------------------------------

@app.route('/profile_page')
def profile_page():
    
    if not current_user.is_authenticated:
        flash('You need to log in to view your profile.', 'error')
        return redirect(url_for('signin_page'))

    
    user = current_user  

   
    return render_template('profile_page.html', user=user)

# ---------------------------------------------------------------------------------------

@app.route('/show_weather')
def show_weather():
    
    return render_template('indi.html')

# ---------------------------------------------------------------------------------------

@app.route('/government_schemes')
def government_schemes():
    return render_template('government_schemes.html')
  
# -------------------------------------------------------------------------------------

@app.route('/set_language', methods=['GET'])
def set_language():
    language = request.args.get('language', 'en')
    session['language'] = language
    return jsonify({'status': 'success', 'language': language})
# ---------------------------------------------------------------------------------------


@app.route('/notifications')
def notifications():
    return render_template('notifications.html', notifications=None) 

@app.route('/notification_bell_click')
def notification_bell_click():
    return redirect(url_for('notifications'))
# -----------------------------------------------------------------------------------------


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        current_weather, forecast_weather, error_message = get_weather_data(city)
        return render_template('indi.html', current_weather=current_weather, forecast_weather=forecast_weather, error_message=error_message)

    return render_template('indi.html', current_weather=None, forecast_weather=None, error_message=None)
# ---------------------------------------------------------------------------------------

def get_weather_data(city):
    api_key = '759f8c8419a3090b77dface5eb5e88aa'
    current_url = 'http://api.openweathermap.org/data/2.5/weather'
    forecast_url = 'http://api.openweathermap.org/data/2.5/forecast'
    
   
    current_params = {'q': city, 'appid': api_key, 'units': 'metric'}
    current_response = requests.get(current_url, params=current_params)
    current_data = current_response.json()

   
    forecast_params = {'q': city, 'appid': api_key, 'units': 'metric'}
    forecast_response = requests.get(forecast_url, params=forecast_params)
    forecast_data = forecast_response.json()

    if current_response.status_code == 200 and forecast_response.status_code == 200:
        current_weather_info = {
            'city': current_data['name'],
            'temperature': current_data['main']['temp'],
            'description': current_data['weather'][0]['description'],
            'icon': current_data['weather'][0]['icon'],
        }

        forecast_weather_info = []
        for forecast in forecast_data['list']:
            forecast_info = {
                'datetime': forecast['dt_txt'],
                'temperature': forecast['main']['temp'],
                'description': forecast['weather'][0]['description'],
                'icon': forecast['weather'][0]['icon'],
            }
            forecast_weather_info.append(forecast_info)

        return current_weather_info, forecast_weather_info, None  

 
    error_message = f"Error: {current_response.status_code} - {current_data.get('message', 'Unknown error')}"
    return None, None, error_message

if __name__ == '__main__':
    with app.app_context():  
        db.create_all()  
    app.secret_key = 'your_secret_key'  
    app.run(debug=True , port=8000)
