from tokens_and_addresses import sql
import os, sys, pymysql
import hashlib, uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, Text, DateTime, VARCHAR, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import exists, select

Base = declarative_base()

class Location(Base):
    __tablename__ = "location"
    id = Column(VARCHAR(36), primary_key=True)
    loc_name = Column(Text, nullable= False)
    latitude = Column(Text, nullable=True)
    longitude = Column(Text, nullable=True)
    coords = Column(Text, nullable=True)

class Commute(Base):
    __tablename__ = "commute"
    id = Column(VARCHAR(36), primary_key=True)
    epoch_time = Column(DateTime, nullable=True)
    start_loc_id = Column(VARCHAR(36), ForeignKey('location.id'))
    dest_loc_id = Column(VARCHAR(36), ForeignKey('location.id'))
    drive_time = Column(Float, nullable=True)
    bus_route = Column(VARCHAR(255), nullable=True)
    bus_time = Column(Float, nullable=True)

# Create and return the database connection
def createSession():
    from sqlalchemy import create_engine
    engine = create_engine("mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(sql['Username'],sql['Password'],sql['Host'],sql['Port'],sql['Database']), echo=False)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    from sqlalchemy.orm import sessionmaker
    DBSession = sessionmaker(bind=engine)
    session = DBSession()  
    session.commit()
    return session

def get_locations(session):
    # Make a query to find all locations in the database and return the dictionary
    return [r.__dict__ for r in session.query(Location).all()]

def get_commutes(session):
    # Make a query to find all commute pairs in the database and return the raw results
    return [r.__dict__ for r in session.query(Commute).all()]

def get_all_commutes_from_db(session):
    commuteData = get_commutes(session)
    commute_dict = []
    for commute in commuteData:
        # This is very slow
        # start_name = session.query(Location).filter(Location.id == commute['start_loc_id']).one().loc_name
        # dest_name = session.query(Location).filter(Location.id == commute['dest_loc_id']).one().loc_name
        start_result = select([Location.loc_name]).where(Location.id == commute['start_loc_id']).execute().fetchone()
        dest_result = select([Location.loc_name]).where(Location.id == commute['dest_loc_id']).execute().fetchone()
        if len(start_result) > 0 and len(dest_result) > 0:
           commute_dict.append({
            'Start Time':commute['epoch_time'],
            'Start Location':start_result[0],
            'Destination Location':dest_result[0],
            'Drive Time':commute['drive_time'],
            'Bus Routes':commute['bus_route'],
            'Bus Time':commute['bus_time']
            })
    return commute_dict

def get_all_commutes_from_db_slow(session):
    commuteData = get_commutes(session)
    commute_dict = []
    for commute in commuteData:
        # This is very slow
        start_name = session.query(Location.loc_name, Location.id).filter(Location.id == commute['start_loc_id']).one().loc_name
        dest_name = session.query(Location.loc_name, Location.id).filter(Location.id == commute['dest_loc_id']).one().loc_name
        commute_dict.append({
            'Start Time':commute['epoch_time'],
            'Start Location':start_name,
            'Destination Location':dest_name,
            'Drive Time':commute['drive_time'],
            'Bus Routes':commute['bus_route'],
            'Bus Time':commute['bus_time']
        })
    return commute_dict

# Get all the commute entries between two locations
def get_commutes_path(session, start, dest):
    return select([Commute]).where(Commute.start_loc_id == start['id']).where(Commute.dest_loc_id == dest['id']).execute().fetchall()

# helper function for importing the old locations database. 
def add_all_locations(session):
    from tokens_and_addresses import locations
    for location in locations:
        add_location_to_db(session, location)

# Add new single location to the database
def add_location_to_db(session,location):
    locationHash = hashlib.md5(str(location['Label']).encode('utf-8')).hexdigest()
    latitude = location['Coords'].split(',')[0].strip()
    longitude = location['Coords'].split(',')[1].strip()
    thisLocation = Location(
        id=locationHash, 
        loc_name=location['Label'], 
        latitude=latitude, 
        longitude=longitude, 
        coords=location['Coords'])
    alreadyThere = session.query(exists().where(Location.id == locationHash)).scalar()
    if alreadyThere == False:
        session.add(thisLocation)
        session.commit()
        print("Added new location {0} to the database".format(thisLocation.loc_name))
    else:
        print("Location already there with same ID")

# Add a new entry to the database
def add_commute_to_db(session, commute):
    thisCommute = Commute(
        id=str(uuid.uuid1()),
        epoch_time = commute['Request Time'],
        start_loc_id = commute['Start_Loc_ID'],
        dest_loc_id = commute['Dest_Loc_ID'],
        drive_time = commute['Drive Time'],
        bus_route = commute['Bus Routes'],
        bus_time = commute['Bus Time'],
    )
    session.add(thisCommute)
    session.commit()
    print("Committed new commute from {0} to {1} into the commute database.".format(thisCommute.start_loc_id, thisCommute.dest_loc_id))

# Run this if we are debugging here.
if __name__ == "__main__":
    session = createSession()
    add_all_locations(session) # Add all teh locations from tokens_and_addresses

    # print(get_locations(session))
    # print(get_commutes(session))

    # Test getting all the location commutes from the database
    allLocations = get_locations(session)
    for n in range(len(allLocations)):
        for m in range(len(allLocations)):
            start = allLocations[n]
            dest = allLocations[m]
            if start != dest:
                get_commutes_path(session, start, dest)

    # Test getting all the entries out of the database
    # get_all_commutes_from_db(session)
    # get_all_commutes_from_db_slow(session)
    session.close()
