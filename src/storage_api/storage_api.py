from geoalchemy2 import load_spatialite

from sqlalchemy import create_engine

from sqlalchemy.event import listen

from .mapping import SatelliteImage

import pysqlite3 as sqlite3

import os

class FileSystemStorage:
    def __init__(self):
        self.cache_path = "cache"
        self.conn = self.initialize() 

    def fetch(self, image_id):
        cursor = self.conn.cursor()
        fetch_query =f"""
                SELECT id, file_path FROM SatelliteImage WHERE id="{image_id}" ;                    
            """
        cursor.execute(fetch_query)
        id, file_path = cursor.fetchone()
        filename = f"{id}.tif"
        with open(f"{file_path}/{filename}", 'rb') as fd:
            file = fd.read()
            return file

    
    def put(self, aoi, date, band_list, image_bytes):

        aoi_in_wkt = "POINT (-65.93254449244697 18.195348751892297)"
        path = f'{os.getcwd()}/{self.cache_path}'
        cursor = self.conn.cursor()
        insert_query ="""
                INSERT INTO SatelliteImage (aoi, date, band_list, file_path) VALUES (
                    ?, ?, ?, ?);                    
            """
        data_to_insert = (
            f"GeomFromText('{aoi_in_wkt}', 4326)",
            date,
            str(band_list),
            path
        )
        cursor.execute(insert_query, data_to_insert)
        self.conn.commit()

        #TODO: Modify id to have database id as file name
        filename = "id.tif"
        #Store image bytes 
        with open(f"{path}/{filename}", 'wb') as fd:
            fd.write(image_bytes)

        return "Success"
    
    def in_storage(self, aoi, date, band_list):
        aoi_in_wkt = "POINT (-65.93254449244697 18.195348751892297)"
        cursor = self.conn.cursor()
        fetch_query =f"""
                SELECT * FROM SatelliteImage 
                WHERE aoi= ? AND date = ? AND band_list = ?;                    
            """
        date_for_query = (
            f"GeomFromText('{aoi_in_wkt}', 4326)", 
            date, 
            str(band_list)
        )
        cursor.execute(fetch_query, date_for_query)
        image_record = cursor.fetchone()[0]
        return image_record
    
    def initialize(self):
        """
        Initializes cache and database 
        """
        #Create cache
        self.initialize_cache()
        #Create connection to db
        cur = self.initialize_db()
        return cur

    def initialize_cache(self):
        if not os.path.exists(f"{os.getcwd()}/{self.cache_path}"):
            try :
                # print()
                os.mkdir(f'{os.getcwd()}/{self.cache_path}')
            
            except :
                raise Exception(f"Failed to create satellite image store")
            
        return 
    
    def initialize_db(self):
        conn = sqlite3.connect('gis.db')
        conn.enable_load_extension(True)
        conn.load_extension("mod_spatialite")
        cur = conn.cursor()
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS SatelliteImage (
                id INTEGER PRIMARY KEY,
                aoi GEOMETRY NOT NULL,
                date TEXT NOT NULL, 
                file_path TEXT NOT NULL,
                band_list TEXT NOT NULL
            );
        '''
        cur.execute(create_table_query)
        return conn
    
    def generate_filename(self, aoi, date, band_list):

        return 
