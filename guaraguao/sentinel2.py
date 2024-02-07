from .earth_engine import earth_engine
import rioxarray as rxr
from io import BytesIO
import json

from typing import List

from typing_json import json

from .storage_api import storage_api
import xarray 


class Sentinel2:
    """
    Class to easily request Sentinel2 images
    Returns the images as rioxarray array
    Uses data downloader to fetch images
    and storage api for caching
    """
    def __init__(self):
        self.storage = storage_api.FileSystemStorage()
        self.data_downloader = earth_engine.EarthEngineAPI()

    def fetch_image(
            self, 
            aoi: json, 
            date: str, 
            band_list: List[str]
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
            store_response = self.storage.in_storage(aoi, date, band_list)
        
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
            self.storage.put(aoi, date, band_list, image_bytes)
            byte_stream = BytesIO(image_bytes)
            #TODO: Add metadata
            return rxr.open_rasterio(byte_stream)
        
        except Exception as e:
            raise e
