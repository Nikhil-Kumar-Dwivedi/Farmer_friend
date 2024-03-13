from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_babel import Babel
import requests

app = Flask(__name__)
babel = Babel(app)

# Define the languages you want to support
LANGUAGES = ['en', 'fr']
app.config['LANGUAGES'] = LANGUAGES

@babel.localeselector
def get_locale():
    # Use language from session, or default to 'en'
    return session.get('language', 'en')

# --------------------------------------------------------------------------------
  
@app.route('/')
def indi():
    return render_template('welcome.html')

# --------------------------------------------------------------------------------

@app.route('/crop_recommendations')
def crop_recommendations():
    # Define hardcoded data for cities and their best crops to grow
    crop_recommendations = [
        {'city': 'City1', 'best_crop': 'Wheat'},
        {'city': 'City2', 'best_crop': 'Rice'},
        {'city': 'City3', 'best_crop': 'Corn'},
        # Add more data as needed
    ]
    return render_template('crop_recommendations.html', crop_recommendations=crop_recommendations)


# ----------------------------------------------------------------------------------------------

@app.route('/soil_profile')
def soil_profile():
    return render_template('soil_profile.html')

# ---------------------------------------------------------------------------------------

@app.route('/next_page')
def next_page():
    # Add logic for handling the next page
    return render_template('next_page.html')

# ---------------------------------------------------------------------------------------


  
@app.route('/show_weather')
def show_weather():
    # Add the logic to display weather information
    return render_template('indi.html')
# ---------------------------------------------------------------------------------------


# @app.route('/soil_profile')
# def soil_profile():
#     # Add the logic to display soil profile information
#     return render_template('soil_profile.html')
# ---------------------------------------------------------------------------------------


@app.route('/government_schemes')
def government_schemes():
    return render_template('government_schemes.html')
  
# -------------------------------------------------------------------------------------

@app.route('/set_language', methods=['GET'])
def set_language():
    language = request.args.get('language', 'en')
    session['language'] = language  # Store the selected language in the session
    return jsonify({'status': 'success', 'language': language})
# ---------------------------------------------------------------------------------------


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
    
    # Current weather data
    current_params = {'q': city, 'appid': api_key, 'units': 'metric'}
    current_response = requests.get(current_url, params=current_params)
    current_data = current_response.json()

    # Forecast data
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

        return current_weather_info, forecast_weather_info, None  # No error

    # Handle errors
    error_message = f"Error: {current_response.status_code} - {current_data.get('message', 'Unknown error')}"
    return None, None, error_message

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'  # Set a secret key for session management
    app.run(debug=True) 