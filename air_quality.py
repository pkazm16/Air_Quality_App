from flask import Flask, render_template, request, redirect
import requests
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from io import BytesIO
import base64


app = Flask(__name__)
# Initialize the Flask application



def get_data(url):
    """Function to get data from REST service."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def test_database_connection():
    """Function to test the connection with the SQLite database."""
    try:
        conn = sqlite3.connect('measurements.db')
        conn.close()
        print("Database connection successful")
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")

def read_data_from_database(station_id):
    """Function for reading data from the database."""
    conn = sqlite3.connect('measurements.db')
    c = conn.cursor()
    c.execute("SELECT * FROM measurements WHERE station_id=?", (station_id,))
    data = c.fetchall()
    conn.close()
    return data


def generate_air_quality_chart(index_levels):
    """Function to generate an air quality chart as an image in Base64 format based on air quality index levels."""
    pollutants = list(index_levels.keys())
    values = [5 if index_levels[p] == 'Bardzo dobry' else
              4 if index_levels[p] == 'Dobry' else
              3 if index_levels[p] == 'Umiarkowany' else
              2 if index_levels[p] == 'Dostateczny' else
              1 for p in pollutants]

    # Create a bar chart
    plt.bar(pollutants, values)
    plt.xlabel('Pollutants')
    plt.ylabel('Air Quality Index')
    plt.title('Air Quality')

    # Convert the chart to an image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return image_base64

geolocator = Nominatim(user_agent="air_quality_app")


@app.route('/') # the home page, which calls the index() function and renders the 'index.html' template
def index():
    """ Function to display the home page."""
    test_database_connection()

    return render_template('index.html')

@app.route('/stations') # a list of measurement stations, which calls the stations() function, fetches data from the REST service, saves station data to the database, and renders the 'stations.html' template.
def stations():
    """Function to display a list of measurement stations obtained from the REST service, save station data to the SQLite database, and render the template with the list of stations."""
    url = 'https://powietrze.gios.gov.pl/pjp-api/rest/station/findAll'
    data = get_data(url)

    formatted_stations = []
    for station in data:
        formatted_station = {
            'id': station['id'],
            'stationName': station['stationName'],
            'gegrLat': station['gegrLat'],
            'gegrLon': station['gegrLon'],
            'city': {
                'id': station['city']['id'],
                'name': station['city']['name'],
                'commune': {
                    'communeName': station['city']['commune']['communeName'],
                    'districtName': station['city']['commune']['districtName'],
                    'provinceName': station['city']['commune']['provinceName']
                }
            },
            'addressStreet': station['addressStreet']
        }
        formatted_stations.append(formatted_station)
        save_to_database(formatted_stations)

    return render_template('stations.html', stations=formatted_stations)


def save_to_database(stations):
    """Function to save station data to the SQLite database."""
    conn = sqlite3.connect('measurements.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS stations_name
                 (id INTEGER PRIMARY KEY, stationName TEXT, gegrLat REAL, gegrLon REAL, cityId INTEGER, 
                 cityName TEXT, communeName TEXT, districtName TEXT, provinceName TEXT, addressStreet TEXT)''')

    for station in stations:
        station_name = station['stationName']
        gegr_lat = station['gegrLat']
        gegr_lon = station['gegrLon']
        city_id = station['city']['id']
        city_name = station['city']['name']
        commune_name = station['city']['commune']['communeName']
        district_name = station['city']['commune']['districtName']
        province_name = station['city']['commune']['provinceName']
        address_street = station['addressStreet']
        c.execute("INSERT INTO stations_name (stationName, gegrLat, gegrLon, cityId, cityName, communeName, districtName, provinceName, addressStreet) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (station_name, gegr_lat, gegr_lon, city_id, city_name, commune_name, district_name, province_name, address_street))

    conn.commit()
    conn.close()
@app.route('/station/<station_id>/') # details of the selected measuring station, calls the station_details(station_id) function and renders the 'station_details.html' template.
def station_details(station_id):
    """Function to display details of a selected measurement station, fetch air quality index data and measurement data, generate a chart, and render the template with the station details, measurements, and the air quality chart."""
    url = f'https://powietrze.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}'
    data = get_data(url)

    index = f'https://powietrze.gios.gov.pl/pjp-api/rest/aqindex/getIndex/{station_id}'
    data_index = get_data(index)
    test_database_connection()
    # measurement data
    measurement_data = f'https://api.gios.gov.pl/pjp-api/rest/data/getData/{station_id}'
    measurement_data = get_data(measurement_data)
    station = []  # Data for station
    measurements = []  # Measurement data
    indexes = []  # Air Quality Index
    date = measurement_data['values']['date'] if 'values' in measurement_data and 'date' in measurement_data[
        'values'] else 'N/A'
    value = measurement_data['values']['value'] if 'values' in measurement_data and 'value' in measurement_data[
        'values'] else 'N/A'

    so2_index_level = data_index['so2IndexLevel']
    if so2_index_level is None :
        so2_index_level_id = 'brak danych'
        index_level_name = 'brak danych '
    else:
        so2_index_level_id = so2_index_level['id']
        index_level_name = so2_index_level['indexLevelName']

    pm25IndexLevel= data_index['pm25IndexLevel']

    if pm25IndexLevel is None:
        pm25IndexLevel_id = 'brak danych'
        pm25IndexLevel_name = 'brak danych '
    else:
        pm25IndexLevel_id = pm25IndexLevel['id']
        pm25IndexLevel_name = pm25IndexLevel['indexLevelName']



    no2IndexLevel= data_index['no2IndexLevel']

    if no2IndexLevel is None:
        no2IndexLevel_id = 'brak danych'
        no2IndexLevel_name = 'brak danych '
    else:
        no2IndexLevel_id = no2IndexLevel['id']
        no2IndexLevel_name = no2IndexLevel['indexLevelName']

    pm10IndexLevel = data_index['pm10IndexLevel']

    if pm10IndexLevel is None:
        pm10IndexLevel_id = 'brak danych'
        pm10IndexLevel_name = 'brak danych '
    else:
        pm10IndexLevel_id = pm10IndexLevel['id']
        pm10IndexLevel_name = pm10IndexLevel['indexLevelName']

    o3IndexLevel= data_index['o3IndexLevel']
    if o3IndexLevel is None:
        o3IndexLevel = 'brak danych'

    else:
        o3IndexLevel = data_index['o3IndexLevel']['indexLevelName'],

    stIndexLevel = data_index['stIndexLevel']
    if stIndexLevel is None:
        stIndexLevelId = 'brak danych'
        indexLevelName = 'brak danych'
    else:
        stIndexLevelId = data_index['stIndexLevel']['id'],
        indexLevelName = data_index['stIndexLevel']['indexLevelName']

    for item in data:
        stIndexCrParam = data_index['stIndexCrParam']

        sensor = {
            'id': item['id'],
            'stationId': item['stationId'],
            'param': {
                'paramName': item['param']['paramName'],
                'paramFormula': item['param']['paramFormula'],
                'paramCode': item['param']['paramCode'],
                'idParam': item['param']['idParam']
            },
            'stCalcDate': data_index['stCalcDate'],
            'stIndexLevel': {
                'stIndexLevelId': stIndexLevelId,
                'indexLevelName': indexLevelName
            },
            'stSourceDataDate': data_index['stSourceDataDate'],
            'so2CalcDate': data_index['so2CalcDate'],
            'so2IndexLevel': {
                'so2IndexLevelId': so2_index_level_id,
                'indexLevelName': index_level_name
            },
            'so2SourceDataDate': data_index['so2SourceDataDate'],
            'no2CalcDate': data_index['no2CalcDate'],
            'no2IndexLevel': {
                'id': no2IndexLevel_id,
                'indexLevelName': no2IndexLevel_name,
            },
            'stIndexCrParam': stIndexCrParam,
            'no2SourceDataDate': data_index['no2SourceDataDate'],
            'pm10CalcDate': data_index['pm10CalcDate'],
            'pm10IndexLevel': {
                'id': pm10IndexLevel_id,
                'indexLevelName': pm10IndexLevel_name
            },

            'pm10SourceDataDate': data_index['pm10SourceDataDate'],
            'pm25CalcDate': data_index['pm25CalcDate'],
            'pm25IndexLevel': {
                'id': pm25IndexLevel_id,
                'indexLevelName': pm25IndexLevel_name
            },
            'pm25SourceDataDate': data_index['pm25SourceDataDate'],
            'o3CalcDate': data_index['o3CalcDate'],
            'o3IndexLevel': o3IndexLevel,
            'o3SourceDataDate': data_index['o3SourceDataDate'],

            'key': measurement_data['key'],
                'values': {
                    'date':date,
                    'value': value
                }
        }

    station.append(sensor)
    save_data_to_database(station, measurement_data)  # Saving data to the database

    # Map the index level names to the corresponding values
    index_levels = {
        'SO2': index_level_name,
        'PM2.5': pm25IndexLevel_name,
        'NO2': no2IndexLevel_name,
        'PM10': pm10IndexLevel_name,
        'O3': o3IndexLevel
    }

    # Call the function to generate the air quality chart
    air_quality_chart = generate_air_quality_chart(index_levels)

    return render_template('station_details.html', station=station, measurements=measurements, indexes=indexes,
                           air_quality_chart=air_quality_chart)


def save_data_to_database(station_data, measurement_data):
    """Function to save station and measurement data to the SQLite database."""
    conn = sqlite3.connect('measurements.db')
    cursor = conn.cursor()

    # Create the necessary tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Stations (
            id INTEGER PRIMARY KEY,
            stationId INTEGER,
            paramName TEXT,
            paramFormula TEXT,
            paramCode TEXT,
            idParam INTEGER,
            stCalcDate TEXT,
            stIndexLevelId INTEGER,
            indexLevelName TEXT,
            stSourceDataDate TEXT,
            so2CalcDate TEXT,
            so2IndexLevelId INTEGER,
            so2IndexLevelName TEXT,
            so2SourceDataDate TEXT,
            no2CalcDate TEXT,
            no2IndexLevelId INTEGER,
            no2IndexLevelName TEXT,
            stIndexCrParam TEXT,
            no2SourceDataDate TEXT,
            pm10CalcDate TEXT,
            pm10IndexLevelId INTEGER,
            pm10IndexLevelName TEXT,
            pm10SourceDataDate TEXT,
            pm25CalcDate TEXT,
            pm25IndexLevelId INTEGER,
            pm25IndexLevelName TEXT,
            pm25SourceDataDate TEXT,
            o3CalcDate TEXT,
            o3IndexLevelName TEXT,
            o3SourceDataDate TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Measurements (
            id INTEGER PRIMARY KEY,
            stationId INTEGER,
            date TEXT,
            value REAL
        )
    ''')

    # Insert or update data in the Stations table
    for item in station_data:
        station_values = (
            item['id'],
            item['stationId'],
            item['param']['paramName'],
            item['param']['paramFormula'],
            item['param']['paramCode'],
            item['param']['idParam'],
            item['stIndexLevel']['indexLevelName'],
            item['stSourceDataDate'],
            item['so2CalcDate'],
            item['so2IndexLevel']['so2IndexLevelId'],
            item['so2IndexLevel']['indexLevelName'],
            item['so2SourceDataDate'],
            item['no2CalcDate'],
            item['no2IndexLevel']['id'],
            item['no2IndexLevel']['indexLevelName'],
            item['stIndexCrParam'],
            item['no2SourceDataDate'],
            item['pm10CalcDate'],
            item['pm10IndexLevel']['id'],
            item['pm10IndexLevel']['indexLevelName'],
            item['pm10SourceDataDate'],
            item['pm25CalcDate'],
            item['pm25IndexLevel']['id'],
            item['pm25IndexLevel']['indexLevelName'],
            item['pm25SourceDataDate'],
            item['o3CalcDate'],
            item['o3SourceDataDate']
        )
        cursor.execute('''
            INSERT OR REPLACE INTO Stations (
                id, stationId, paramName, paramFormula, paramCode, idParam,
                indexLevelName, stSourceDataDate, so2CalcDate, so2IndexLevelId, so2IndexLevelName,
                so2SourceDataDate, no2CalcDate, no2IndexLevelId, no2IndexLevelName, stIndexCrParam,
                no2SourceDataDate, pm10CalcDate, pm10IndexLevelId, pm10IndexLevelName, pm10SourceDataDate,
                pm25CalcDate, pm25IndexLevelId, pm25IndexLevelName, pm25SourceDataDate, o3CalcDate,
                o3SourceDataDate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', station_values)

    # Insert data into the Measurements table
    try:
        for measurement in measurement_data['values']:
            measurement_values = (
                measurement_data['key'],
                measurement['date'] if 'date' in measurement else 'N/A',
                measurement['value'] if 'value' in measurement else 'N/A'
            )
            cursor.execute('''
                INSERT INTO Measurements (stationId, date, value)
                VALUES (?, ?, ?)
            ''', measurement_values)
    except Exception:
        pass

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


@app.route('/map') # displays a map with marked measurement stations, which calls the map() function, fetches data from the REST service, and renders the 'map.html' template with the map and station markers
def map():
    """Function to display a map with marked measurement stations obtained from the REST service and render the template with the map and station markers."""
    url = 'https://powietrze.gios.gov.pl/pjp-api/rest/station/findAll'
    data = get_data(url)

    formatted_stations = []
    for station in data:
        formatted_station = {
            'id': station['id'],
            'stationName': station['stationName'],
            'gegrLat': station['gegrLat'],
            'gegrLon': station['gegrLon'],
            'city': {
                'id': station['city']['id'],
                'name': station['city']['name'],
                'commune': {
                    'communeName': station['city']['commune']['communeName'],
                    'districtName': station['city']['commune']['districtName'],
                    'provinceName': station['city']['commune']['provinceName']
                }
            },
            'addressStreet': station['addressStreet']
        }
        formatted_stations.append(formatted_station)

    return render_template('map.html', stations=formatted_stations)



@app.route('/stations/nearby', methods=['GET', 'POST']) # displays measurement stations near a specified location, handling both GET and POST requests, calling the stations_nearby() function, and rendering the 'nearby.html' template
def stations_nearby():
    """a function to display measurement stations near a specified location based on geographic coordinates obtained from a form, fetch data from the REST service, and render the template with the list of stations nearby."""
    if request.method == 'POST':
        location = request.form['location']
        radius = float(request.form['radius'])
        geolocation = geolocator.geocode(location)
        if not geolocation:
            return render_template('nearby.html', error='Invalid location')
        lat, lon = geolocation.latitude, geolocation.longitude
        url = f'https://powietrze.gios.gov.pl/pjp-api/rest/station/findAll'
        data = get_data(url)
        filtered_stations = []
        for station in data:
            station_id = station['id']
            station_lat = station['gegrLat']
            station_lon = station['gegrLon']
            distance = geodesic((lat, lon), (station_lat, station_lon)).km
            if distance <= radius:
                filtered_stations.append(station)
        return render_template('stations_nearby.html', stations=filtered_stations, location=location, radius=radius)
    return render_template('nearby.html')



if __name__ == '__main__':
    app.run(debug=True)