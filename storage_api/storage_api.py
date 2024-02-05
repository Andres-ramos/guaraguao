from geoalchemy2 import load_spatialite

from sqlalchemy import create_engine

from sqlalchemy.event import listen

from .mapping import SatelliteImage

import pysqlite3 as sqlite3

# import sqlite3

class FileSystemStorage:
    def __init__(self):
        self.path = "./cache"
        self.conn = self.initialize() 
        print(SatelliteImage) 

    def fetch(self):
        print("hola")
        return 
    
    def put(self, image_bytes):
        #Put image in file system cache
        #Put entry in the database 
        return 
    
    def in_storage(self):
        #Check db to see if file there
        #Check in terms of the bands, date and aoi
        return 
    
    def initialize(self):
        #Create connection to db
        #Check if tables are created
        #Otherwies creates them
        #Returns connection
        conn = sqlite3.connect('gis.db')
        conn.enable_load_extension(True)
        conn.load_extension("mod_spatialite")

        # engine = create_engine("sqlite:///gis.db", echo=True)

        # listen(engine, "connect", load_spatialite)

        # conn = engine.connect()

        return conn
