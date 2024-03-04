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


class Sentinel2:
    """
    Class to easily request Sentinel2 images
    Returns the images as rioxarray array
    Uses data downloader to fetch images
    and storage api for caching
    """
    def __init__(self, cache_name="cache", collection='COPERNICUS/S2_SR_HARMONIZED'):
        self.collection = collection
        self.storage = storage_api.FileSystemStorage(cache_name)
        self.data_downloader = earth_engine.EarthEngineAPI(collection)
        self.copernicus_client = copernicus.CopernicusClient("SENTINEL-2")
        self.satellite_name = "SENTINEL-2"

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
            aoi: geojson, 
            date: str, 
            band_list: List[str]

        Output: 
            Rioxarray with image
        """
        #Checks storage
        try :
            store_response = self.storage.in_storage(
                aoi, 
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
                aoi, date, band_list
            )
            #puts file in storage
            self.storage.put(
                aoi, 
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

    #TODO: Make this method better
    def fetch_storage_path(
            self, 
            aoi: json, 
            date: str, 
            band_list: List[str]
        ) -> str:
        """
        Fetches the path where the image is stored
        Image must be in storage
        """
        try :
            store_response = self.storage.in_storage(
                aoi, 
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
            self.storage.put(aoi, date, band_list, image_bytes)
            store_response = self.storage.in_storage(aoi, date, band_list)
            return store_response["path"]

        except Exception as e:
            raise e
        
    def check_available_images(
            self, 
            aoi: json, 
            date_start: str,
            date_end: str
            ) -> Dict[str, any]:
        return pd.DataFrame(self.copernicus_client.check_available_files(aoi, date_start, date_end))