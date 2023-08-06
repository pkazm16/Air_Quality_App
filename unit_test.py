import unittest
import sqlite3
from unittest.mock import patch
from air_quality import app, get_data, save_data_to_database, read_data_from_database, test_database_connection

class AppTestCase(unittest.TestCase):
    """Test case for the Flask application."""

    def setUp(self):
        """Set up the test client and enable testing mode for the Flask app."""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        """Test the index route '/'.
        This test ensures that the index route returns a 200 status code."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_stations_route(self):
        """Test the stations route '/stations'.
        This test ensures that the stations route returns a 200 status code."""
        response = self.app.get('/stations')
        self.assertEqual(response.status_code, 200)


    @patch('air_quality.get_data')
    def test_station_details_route(self, mock_get_data):
        """Test the station details route '/station/<station_id>'."""
        mock_get_data.return_value = {
            'pm25IndexLevel': {
                'id': 1,
                'indexLevelName': 'brak danych'
            },
            'pm25IndexLevel': {
                'id': 2,
                'indexLevelName': 'brak danych'
            },

        }
        response = self.app.get('/station/114')
        self.assertEqual(response.status_code, 308)

    def test_map_route(self):
        """Test the map route '/map'.
        This test ensures that the map route returns a 200 status code."""
        response = self.app.get('/map')
        self.assertEqual(response.status_code, 200)


    def test_stations_nearby_route(self):
        """Test the stations nearby route '/stations/nearby'.
         This test ensures that the stations nearby route returns a 200 status code."""
        response = self.app.post('/stations/nearby', data={'location': 'New York', 'radius': '10'})
        self.assertEqual(response.status_code, 200)


class DatabaseTestCase(unittest.TestCase):
    """Test case for database-related functions."""

    def setUp(self):
        """Set up an in-memory SQLite database for testing."""
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()

        # Create the necessary tables
        self.cursor.execute('''
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

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Measurements (
                id INTEGER PRIMARY KEY,
                stationId INTEGER,
                date TEXT,
                value REAL
            )
        ''')

    def tearDown(self):
        """Close the database connection."""
        self.cursor.close()
        self.conn.close()

    def test_save_data_to_database(self):
        """This test ensures that the save_data_to_database function stores data
        into the in-memory database correctly."""
        station_data = [
            {
                'id': 1,
                'stationId': 123,
                'param': {
                    'paramName': 'Param1',
                    'paramFormula': 'Formula1',
                    'paramCode': 'Code1',
                    'idParam': 1
                },
                'stIndexLevel': {
                    'indexLevelName': 'Level1'
                },

                'so2IndexLevel': {
                    'so2IndexLevelId': 1,
                    'indexLevelName': 'index_level_name'
                },
                'so2SourceDataDate': 'b',
                'no2CalcDate': 'a',
                'no2IndexLevel': {
                    'id': 1,
                    'indexLevelName': 'no2IndexLevel_name',
                },
                'stIndexCrParam': 'stIndexCrParam',
                'no2SourceDataDate': 'a',
                'pm10CalcDate': 'dadasd',
                'pm10IndexLevel': {
                    'id': 123,
                    'indexLevelName': 'pm10IndexLevel_name'
                },

                'pm10SourceDataDate': 'asdasdasd',
                'pm25CalcDate':'adadad',
                'pm25IndexLevel': {
                    'id': 1233,
                    'indexLevelName': 'pm25IndexLevel_name'
                },
                'pm25SourceDataDate': 'asdasdasd',
                'o3CalcDate': 'adadad',
                'o3IndexLevel': "o3IndexLevel",

                'o3SourceDataDate': "SASDAD",
                # Add other required keys/values
                'stSourceDataDate':'stSourceDataDate',
                'so2CalcDate':'so2CalcDate'
            }
        ]
        measurement_data = {
            'key': 123,
            'values': [
                {
                    'date': '2023-06-26',
                    'value': 10.5
                }
            ]
        }

        # Call the function being tested
        save_data_to_database(station_data, measurement_data)


        self.cursor.execute('SELECT * FROM Stations')
        stations_rows = self.cursor.fetchall()
        self.assertEqual(len(stations_rows), 0)

        self.cursor.execute('SELECT * FROM Measurements')
        measurements_rows = self.cursor.fetchall()
        self.assertEqual(len(measurements_rows), 0)


