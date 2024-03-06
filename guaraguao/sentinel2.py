from .earth_engine import earth_engine
from .copernicus import copernicus

from .storage_api import storage_api

import rioxarray as rxr
from io import BytesIO
import json

from typing import List, Dict

from typing_json import json

import xarray 
import pandas as pd
import datetime


class Sentinel2:
    """
    Class to easily request Sentinel2 images
    Returns the images as rioxarray array
    Uses data downloader to fetch images
    and storage api for caching
    """
    def __init__(self, cache_name="cache", collection='S2_SR_HARMONIZED'):
        self.satellite_name = "COPERNICUS"
        self.collection = collection
        self.storage = storage_api.FileSystemStorage(cache_name)
        self.data_downloader = earth_engine.EarthEngineAPI(f"{self.satellite_name}/{self.collection}")
        self.copernicus_client = copernicus.CopernicusClient("SENTINEL-2")
        

    def fetch_image(
            self, 
            aoi: json, 
            date: str, 
            band_list: List[str] = ['B1','B2', 'B3', 'B4', 'B5', 'B6', 'B7',
             'B8', 'B8A','B9', 'B11', 'B12']
        ) -> xarray.Dataset:
        """
        Fetches image from data source or from cache
        Input: 
            aoi: geojson (FeatureCollection | Polygon), 
            date: str, 
            band_list: List[str]

        Output: 
            Rioxarray with image
        """
        #Checks storage
        polygon_aoi = self.process_aoi(aoi)
        print(polygon_aoi)
        try :
            store_response = self.storage.in_storage(
                polygon_aoi, 
                date, 
                band_list, 
                self.collection, 
                self.satellite_name
            )
        
        except Exception as e:
            raise e
        #If file in storage returns files
        if store_response["in_storage"]:
            image_id = store_response["id"]
            try :
                store_response = self.storage.fetch(image_id)
                image_bytes = store_response["image_bytes"]
                byte_stream = BytesIO(image_bytes)
                #TODO: Add metadata to rioxarray
                return rxr.open_rasterio(byte_stream)
            
            except Exception as e:
                raise e
        #If file not in storage, fetches, stores and returns
        try :
            #Fetches file 
            image_bytes = self.data_downloader.fetch_image_bytes(
                polygon_aoi, date, band_list
            )
            #puts file in storage
            self.storage.put(
                polygon_aoi, 
                date, 
                band_list,
                self.collection, 
                self.satellite_name,
                image_bytes
            )
            byte_stream = BytesIO(image_bytes)
            #TODO: Add metadata
            return rxr.open_rasterio(byte_stream)
        
        except Exception as e:
            raise e

    def fetch_storage_path(
            self, 
            aoi: json, 
            date: str, 
            band_list: List[str] = ['B1','B2', 'B3', 'B4', 'B5', 'B6', 'B7',
             'B8', 'B8A','B9', 'B11', 'B12']
        ) -> str:
        """
        Fetches the path where the image is stored
        Image must be in storage
        """
        polygon_aoi = self.process_aoi(aoi)
        try :
            store_response = self.storage.in_storage(
                polygon_aoi, 
                date, 
                band_list, 
                self.collection, 
                self.satellite_name
            )
            #If file is in storaage
            if store_response["in_storage"]:
                return store_response["path"]
            
            #Otherwise download file
            image_bytes = self.data_downloader.fetch_image_bytes(
                aoi, date, band_list
            )
            #puts file in storage
            self.storage.put(
                polygon_aoi, 
                date, 
                band_list,
                self.collection,
                self.satellite_name,
                image_bytes
            )
            #Gets storage path
            store_response = self.storage.in_storage(
                polygon_aoi, 
                date, 
                band_list, 
                self.collection, 
                self.satellite_name
            )
            return store_response["path"]

        except Exception as e:
            raise e
        
    def check_available_images(
            self, 
            aoi: json, 
            start_date: str,
            end_date: str
        ) -> Dict[str, any]:
        """
        Return dataframe of files in a given date range
        """
        try :
            collection = self.data_downloader.get_image_dates(
                aoi,
                start_date, 
                end_date
            )
        
        except Exception as e:
            raise Exception("ERROR: Fetch available files")
        

        features =  collection["features"]
        image_entries = [self.generate_image_row(
            features[i]["properties"]
            )for i in range(len(features))
        ]
        return pd.DataFrame(image_entries)
    
    def generate_image_row(self,properties:json) -> Dict[str, str]:
        """
        Generate and image entry row
        Input : properties json
        Output: image entry dict

        {
            satellite_name: str,
            datetime: str
        }
        """
        #TODO: Add more metadata from properties
        gen_time = properties["GENERATION_TIME"]
        timestamp = (gen_time/1000)
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return {
            "satellite_name": properties["SPACECRAFT_NAME"],
            "date": f"{dt_object.year}-{dt_object.month}-{dt_object.day}",
            "time": f"{dt_object.hour}:{dt_object.minute}:{dt_object.second}"
        }
    
    def process_aoi(self, aoi:json) -> json:
        """
        Processes aoi to be in polygon type
        Input: geojson aoi,
        Output: Polygon geojson
        """
        geom_type = aoi["type"]
        processing_functions = {
            "FeatureCollection": lambda feature_collection : feature_collection['features'][0]['geometry'],
            "Polygon": lambda polygon: polygon
        }
  
        return processing_functions[geom_type](aoi)