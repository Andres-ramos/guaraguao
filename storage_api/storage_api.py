from geoalchemy2 import load_spatialite

from sqlalchemy import create_engine

from sqlalchemy.event import listen

import sqlite3

class FileSystemStorage:
    def __init__(self):
        self.path = "./cache"
        self.conn = self.initialize()  

    def fetch(self):
        return 
    
    def put(self, image_bytes):
        
        return 
    
    def in_storage(self):
        return 
    
    def initialize(self):
        engine = create_engine("sqlite:///gis.db", echo=True)

        listen(engine, "connect", load_spatialite)

        conn = engine.connect('gis.db')

        return conn
