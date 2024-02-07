import pysqlite3 as sqlite3

import os

from typing import Dict, List

from typing_json import json

from shapely.geometry import shape

import shapely 

class FileSystemStorage:
    """
    Implements file system storage
    Has a spatiallite database to record which satellite images
    are on record
    Uses file system to store images
    """
    def __init__(self):
        self.cache_path = "cache"
        self.conn = self.initialize() 

    def fetch(self, image_id:str) -> Dict[str, any]:
        """
        Fetches image bytes by image id
        Return {
            success: bool,
            in_storage: bool,
            image_bytes: None | bytes
        }
        """
        cursor = self.conn.cursor()
        fetch_query =f"""
                SELECT id, file_path FROM SatelliteImage WHERE id="{image_id}" ;                    
            """
        cursor.execute(fetch_query)
        id, file_path = cursor.fetchone()
        filename = f"{id}.tif"
        with open(f"{file_path}/{filename}", 'rb') as fd:
            file = fd.read()

        return {
            "success": True, 
            "in_storage": True,
            "image_bytes": file
        }

    
    def put(
            self, 
            aoi:json, 
            date:str, 
            band_list: List[str], 
            image_bytes: any
        ) -> Dict[str, any]:
        """
        Puts image information in db and file system storage
        """
        aoi_in_wkt = shapely.to_wkt(shape(aoi["features"][0]["geometry"]))
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

        filename = f"{cursor.lastrowid}.tif"

        #Store image bytes 
        with open(f"{path}/{filename}", 'wb') as fd:
            fd.write(image_bytes)

        return {
            "success": True,
            "id": cursor.lastrowid
        }
    
    def in_storage(
            self, 
            aoi: json, 
            date: str, 
            band_list: List[str]
        ) -> Dict[str, any]:

        aoi_in_wkt = shapely.to_wkt(shape(aoi["features"][0]["geometry"]))
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
        image_record = cursor.fetchone()
        if image_record:
            return {
                "sucess": True, 
                "in_storage": True,
                "id": image_record[0]
                }
        else :
            return {
                "sucess": True, 
                "in_storage": False,
                "id": None
            }
    
    #Initialization part 
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
        """
        Checks if cache folder has been created
        Uses cache name specified in class initializer
        """
        if not os.path.exists(f"{os.getcwd()}/{self.cache_path}"):
            try :
                os.mkdir(f'{os.getcwd()}/{self.cache_path}')
            
            except :
                raise Exception(f"Failed to create satellite image store")
            
        return 
    
    def initialize_db(self) -> sqlite3.connect:
        """
        Initializes the database connection
        Create satellite image table if not created
        """
        #TODO: Figure out if this is the best way to do this? 
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
