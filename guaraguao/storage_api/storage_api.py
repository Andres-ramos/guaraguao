import sqlite3

import os

from typing import Dict, List

from typing_json import json

from shapely.geometry import shape

import shapely 

from .db import get_db, init_db

import os.path

class FileSystemStorage:
    """
    Implements file system storage
    Has a spatiallite database to record which satellite images
    are on record
    Uses file system to store images
    """
    def __init__(self, cache="cache"):
        self.cache_path = cache
        self.db = self.initialize(cache) 

    def fetch(self, image_id:str) -> Dict[str, any]:
        """
        Fetches image bytes by image id
        Return {
            success: bool,
            in_storage: bool,
            image_bytes: None | bytes
        }
        """
        # cursor = self.conn.cursor()
        fetch_query =f"""
                SELECT * FROM SatelliteImage WHERE id="{image_id}" ;                    
            """
        #Fetches image row
        cursor = self.db.cursor()
        cursor.execute(fetch_query)
        image_db_entry = cursor.fetchone()

        #Extracts relevant data from row
        id = image_db_entry[0]
        file_path = image_db_entry[3]
        metadata = eval(image_db_entry[-1])

        #Reads file bytes
        filename = f"{id}.tif"
        with open(f"{file_path}/{filename}", 'rb') as fd:
            file = fd.read()

        return {
            "success": True, 
            "in_storage": True,
            "image_bytes": file,
            "image_metadata": metadata
        }

    
    def put(
            self, 
            aoi_polygon:json, 
            date:str, 
            band_list: List[str], 
            collection: str,
            satellite: str,
            image_bytes: any,
            image_metadata : Dict[str,any],
        ) -> Dict[str, any]:
        """
        Puts image information in db and file system storage
        """
        aoi_in_wkt = shapely.to_wkt(shape(aoi_polygon))
        path = f'{os.getcwd()}/{self.cache_path}'
        cursor = self.db.cursor()
        insert_query ="""
                INSERT INTO SatelliteImage (aoi, date, band_list, file_path, collection, satellite, metadata) VALUES (
                    ?, ?, ?, ?, ?, ?, ?);                    
            """
        #Inserts image_metadata... 
        #TODO: Normalize metadata
        #TODO: Correct solution is to add metadata table.... 
        data_to_insert = (
            f"GeomFromText('{aoi_in_wkt}', 4326)",
            date,
            str(band_list),
            path,
            collection,
            satellite,
            str(image_metadata)
        )
        cursor.execute(insert_query, data_to_insert)
        self.db.commit()

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
            aoi_polygon: json, 
            date: str, 
            band_list: List[str],
            collection: str,
            satellite: str
        ) -> Dict[str, any]:

        aoi_in_wkt = shapely.to_wkt(shape(aoi_polygon))
        cursor = self.db.cursor()
        fetch_query =f"""
                SELECT * FROM SatelliteImage 
                WHERE aoi= ? AND date = ? AND band_list = ? AND collection = ? AND satellite = ?;                    
            """
        date_for_query = (
            f"GeomFromText('{aoi_in_wkt}', 4326)", 
            date, 
            str(band_list),
            collection,
            satellite
        )
        cursor.execute(fetch_query, date_for_query)
        image_record = cursor.fetchone()

        if image_record:
            image_id = image_record[0]
            path = f"{image_record[3]}/{image_id}.tif"
            return {
                "sucess": True, 
                "in_storage": True,
                "id": image_id,
                "path": path
                }
        else :
            return {
                "sucess": True, 
                "in_storage": False,
                "id": None,
                "path": None
            }
    
    #Initialization part 
    def initialize(self, db_name):
        """
        Initializes cache and database 
        """
        #Create cache
        self.initialize_cache()
        #Checks if db file exists
        if not os.path.isfile(db_name):
            db = init_db(db_name)
        #gets db connection object
        db = get_db(db_name)

        return db

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
