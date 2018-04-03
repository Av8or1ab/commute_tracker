import googlemaps, datetime, time
import pytz
from dbConnector import get_locations, add_all_locations, add_commute_to_db, createSession, get_all_commutes_from_db
import tokens_and_addresses

# Get the fastest bus route from the list of options
def get_fastest_transit(transit_directions_list, now_epoch):
    """
    Returns fastest bus route and time based on current time

    :param transit_directions_list: List of Google Maps Directions objects each containing
    transit directions between source and destination
    :type transit_directions_list: List of Google Maps Directions objects
    """
    bus_trip = {
        'Bus Route List':'None',
        'Bus Transit Time': float('-3.402823466E+38'),
        'Bus Longest Leg':'None'
        }

    if len(transit_directions_list) < 1: 
        return bus_trip

    fastest_transit_dir = transit_directions_list[0]
    fastest_transit_dir_time = (transit_directions_list[0]['legs'][0]['arrival_time']['value'] - now_epoch) / 60
    for dirobj in transit_directions_list:
        temp_dir_time = (dirobj['legs'][0]['arrival_time']['value'] - now_epoch) / 60
        if temp_dir_time < fastest_transit_dir_time:
            fastest_transit_dir = dirobj
            fastest_transit_dir_time = temp_dir_time

    fastest_dir_steps = fastest_transit_dir['legs'][0]['steps']
    primary_step = fastest_dir_steps[0]
    primary_step_time = 0
    full_bus_route = []
    for step in fastest_dir_steps:
        if step['travel_mode'] == 'TRANSIT':
            full_bus_route.append(step['transit_details']['line']['short_name'])
            temp_step_time = int(step['duration']['value'])
            if temp_step_time > primary_step_time:
                primary_step = step
                primary_step_time = temp_step_time
          
    bus_trip['Bus Route List'] = '->'.join(full_bus_route)
    bus_trip['Bus Transit Time'] = round(fastest_transit_dir_time, 1)
    bus_trip['Bus Longest Leg'] = primary_step['transit_details']['line']['short_name']
    return bus_trip

# Get the commute data between two locations via driving and the bus
def get_commute(start, dest, now_local):
    # Create the google maps client connection
    gmaps_client = googlemaps.Client(key=tokens_and_addresses.google_maps_directions_api_key)
    # Get the drive commute
    commute_drive = gmaps_client.directions(start['coords'], dest['coords'], departure_time=now_local)
    if len(commute_drive) > 0 and len(commute_drive[0]['legs']) > 0:
        drive_time = round(commute_drive[0]['legs'][0]['duration_in_traffic']['value'] / 60, 1)
    else:
        drive_time = float("-3.402823466E+38")
    # Get the bus commute
    commute_transit = gmaps_client.directions(start['coords'], dest['coords'], departure_time=now_local, mode='transit', transit_mode='bus', alternatives=True)
    fastest_transit = get_fastest_transit(commute_transit, int(time.time()))

    return {
        "Start_Loc_ID":start['id'],
        "Dest_Loc_ID":dest['id'],
        "Request Time":time.strftime("%Y-%m-%d %H:%M:%S"),
        "Drive Time":drive_time,
        "Bus Routes":fastest_transit['Bus Route List'],
        "Bus Time":fastest_transit['Bus Transit Time'],
        }

# Get the commute data for all the locations in the tokens and addresses file.
def get_all_commutes(json_data, context):
    try:
        now_object = datetime.datetime
        now = now_object.now()
        timezone = pytz.timezone("America/Los_Angeles")
        now_local = timezone.localize(now)
        print(now_local)

        dbSession = createSession()
        
        locations = get_locations(dbSession)
        if len(locations) < 1:
            add_all_locations(dbSession)
            locations = get_locations(dbSession)

        commutes = []
        for start in locations:
            for dest in locations:
                if start != dest:
                    new_commute = get_commute(start, dest, now_local)
                    commutes.append(new_commute)
                    add_commute_to_db(dbSession, new_commute)
                    time.sleep(1)
        return commutes                    
    
    except KeyError as e1:
        print('KeyError, missing dictionary key: ', e1)

# Run htis if we are debugging here.
if __name__ == "__main__":
    get_all_commutes(None, None)