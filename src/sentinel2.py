from .earth_engine import earth_engine
import rioxarray as rxr
from io import BytesIO
import json

from typing import List

from typing_json import json

from .storage_api import storage_api


class Sentinel2:

    def __init__(self):
        self.storage = storage_api.FileSystemStorage()
        self.data_downloader = earth_engine.EarthEngineAPI()


    #TODO: Implement once requierements are ironed out
    def fetch_images(self, aoi, search_start, search_end, bands_list):
        return 

    #TODO: Implement storage mechanism
    def fetch_image(
            self, 
            aoi: json, 
            date: str, 
            band_list: List[str]
        ):
        """
        Input: 
            aoi: geojson, 
            date: str, 
            band_list: List[str]
        """
        #TODO: Check storage
        in_storage = self.storage.in_storage(aoi, date, band_list)
        print(in_storage)
        # if in_storage:
        #     image_id = 3
        #     image_bytes = self.storage.fetch(image_id)
        #     byte_stream = BytesIO(image_bytes)
        #     return rxr.open_rasterio(byte_stream)

        # else :
        #     try :
        #         image_bytes = self.data_downloader.fetch_image_bytes(
        #             aoi, date, band_list
        #         )
        #         self.storage.put(aoi, date, band_list, image_bytes)
        #         byte_stream = BytesIO(image_bytes)
        #         return rxr.open_rasterio(byte_stream)
            
        #     except Exception as e:
        #         raise e

    def seed_db(self):
        self.storage.fetch()
        return 
