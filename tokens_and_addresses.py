'''
Fill in details for ‘sql_host’, ‘sql_username’, ’sql_password’, ‘google_maps_directions_api_key’, and ‘home_coords’
'''

# use_sqllite = False
sql = {
    'Username': 'josh',
    'Password': 'w0rkSucks',
    'Host': 'app.nwengineer.com', # '127.0.0.1',
    'Port': 3306 , # 3306 is default for MySql
    'Database': 'commuteTracker',
}

# API Key for google maps integration
google_maps_directions_api_key = 'AIzaSyAF_tL86QTqheHxXoGoRJI74O2Tmd0Q974'

# Coordinates in the form of 'Lat, Lon' for testing purposes
locations = [
    {'Label':'Home','Coords':'47.782210, -122.174198'},
    {'Label':'Seattle','Coords':'47.609875, -122.337941'},
    {'Label':'Ballard','Coords':'47.6792172,-122.38603119999999'},
    {'Label':'Wellspring', 'Coords':'47.58573,-122.30341199999998'},
    {'Label':'Evergreen Hospital','Coords':'47.7158374,-122.177841'},
    {'Label':'Electroimpact','Coords':'47.8960222,-122.29794370000002'},
    {'Label':'Boeing Everett', 'Coords':'47.92652210000001,-122.27207220000003'},
    {'Label':'Boeing Renton', 'Coords':'47.5004577,-122.20728610000003'},
    {'Label':'Chad\'s Boat', 'Coords':'47.65187946757743,-122.32316672801971'},
    {'Label':'Dan\'s House', 'Coords':'47.724834701845325,-122.35943790972794'}
        ]