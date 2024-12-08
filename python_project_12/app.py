import requests
from flask import *

app = Flask(__name__)

# Ваш API-ключ
API_KEY = ''

# Функция для получения данных о погоде из AccuWeather API
def get_weather_data(city):
    try:
        # Получаем код города
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}"
        location_response = requests.get(location_url)
        location_data = location_response.json()
        city_key = location_data[0]['Key']

        # Получаем погодные данные для города
        weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{city_key}?apikey={API_KEY}"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        # Извлекаем нужные параметры
        temperature = weather_data[0]['Temperature']['Metric']['Value']
        humidity = weather_data[0]['Humidity']
        wind_speed = weather_data[0]['Wind']['Speed']['Metric']['Value']
        precipitation = weather_data[0]['PrecipitationSummary']['PastHour']['Metric']['Value']

        return {
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'precipitation': precipitation
        }

    except Exception as e:
        return {'error': str(e)}

# Функция для оценки погодных условий
def check_weather(weather_data):
    if 'error' in weather_data:
        return 'Ошибка при получении данных о погоде.'

    temperature = weather_data['temperature']
    wind_speed = weather_data['wind_speed']
    precipitation = weather_data['precipitation']

    # Пороговые значения для плохой погоды
    if temperature < 0 or temperature > 35:
        return 'Плохая погода: температура слишком низкая или высокая.'
    elif wind_speed > 50:
        return 'Плохая погода: слишком сильный ветер.'
    elif precipitation > 5:
        return 'Плохая погода: сильные осадки.'
    else:
        return 'Погода хорошая.'

# Главная страница с формой для ввода городов
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        start_city = request.form['start_city']
        end_city = request.form['end_city']

        # Получаем погоду для стартового города
        start_weather = get_weather_data(start_city)
        end_weather = get_weather_data(end_city)

        # Оценка погодных условий
        start_weather_condition = check_weather(start_weather)
        end_weather_condition = check_weather(end_weather)

        return render_template('index.html', start_weather_condition=start_weather_condition,
                               end_weather_condition=end_weather_condition, start_city=start_city, end_city=end_city)

    return render_template('index.html', start_weather_condition=None, end_weather_condition=None)

if __name__ == '__main__':
    app.run(debug=True)
