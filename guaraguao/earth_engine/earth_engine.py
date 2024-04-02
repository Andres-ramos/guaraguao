import ee
import numpy as np
import pandas as pd
import io 
import requests 
import json
import shapely

from .exceptions import EarthEngineNoAvailableFile
from .exceptions import EarthEngineFileDownloadException

from typing import List
from typing import Dict

from .constants import EarthEngineConstants

class EarthEngineAPI:
    def __init__(self, collection):
        self.initialize()
        self.sentinel_collection = collection
    
    def fetch_image_bytes(
            self, 
            aoi_polygon: json, 
            date:str, 
            band_list: List[str]
        ):
        '''
        Fetches image
        Input: 
            aoi_polygon - aoi polygon in geojson format
            date - date "yyyy-mm-dd" format
            band_list -
        Output :
            geotiff bytes 
        '''
        #Converts geojson to ee polygon
        ee_aoi = self.get_aoi(aoi_polygon)
        #Fetches the image
        ee_image = self.get_image(date, ee_aoi)
        #Downloads the image bytes
        geotiff_bytes = self.to_geotiff_bytes(ee_image, band_list)
        return geotiff_bytes

    def get_image(
            self,
            date: str,
            ee_polygon: ee.Geometry.Polygon
        ):
        '''
        Method that returns image in aoi for a given day
        Note: Mosaics images if AOI spans more than one image
        Input: 
            datetime - "yyyy-mm-dd" format
            ee_polygon - ee polygon of aoi
        Output: 
            ee image output
        '''
        start_date = pd.to_datetime(date)
        end_date = start_date + pd.Timedelta(1, "d")
        collection = ee.ImageCollection(
            self.sentinel_collection).filterDate(
                ee.Date(start_date), 
                ee.Date(end_date)
                ).filterBounds(ee_polygon)
        if collection.size().getInfo() > 1:
            image = collection.mosaic()
            return image.clip(ee_polygon)
        
        elif collection.size().getInfo() == 1:
            return collection.first().clip(ee_polygon)

        raise EarthEngineNoAvailableFile
    
    def get_aoi(
            self, 
            aoi_polygon: json
        ):
        """
        Converts polygon geojson to ee polygon
        """
        coords = aoi_polygon['coordinates']
        return ee.Geometry.Polygon(coords)
    
    def to_geotiff_bytes(
            self, 
            ee_image, 
            bands_list
        ):
        '''
        Returns geotiff bytes of image
        Input:
            ee_image - ee image object
            bands_list - [] 
        Output:
            numpy arr with shape height x width x bands 
        '''
        scale = 10
        ee_image_aoi = ee_image.geometry().getInfo()
        url = ee_image.getDownloadUrl({
            'bands': bands_list,
            'region': ee_image_aoi,
            'scale': scale,
            'format': 'GEO_TIFF',
            'crs': 'EPSG:4326'
        })
        try :
            response = requests.get(url)
            return response.content 
        
        except Exception as e:
            raise EarthEngineFileDownloadException from e

    def to_numpy_bytes(self, ee_image, band_list):
        scale = 10
        ee_image_aoi = ee_image.geometry().getInfo()
        url = ee_image.getDownloadUrl({
            'bands': band_list,
            'region': ee_image_aoi,
            'scale': scale,
            'format': 'NPY'
        })
        try :
            response = requests.get(url)
            return response.content 
        
        except Exception as e:
            raise EarthEngineFileDownloadException from e

    def to_numpy(self, ee_image, band_list):

        scale = 10        
        ee_image_aoi = ee_image.geometry().getInfo()
        url = ee_image.getDownloadUrl({
            'bands': band_list,
            'region': ee_image_aoi,
            'scale': scale,
            'format': 'NPY'
        })
        try :
            response = requests.get(url)
            data = np.load(io.BytesIO(response.content))
            return data
        
        except Exception as e:
            raise EarthEngineFileDownloadException from e
        
    def initialize(self):
        """
        Authenticates earth engine
        """
        service_account = EarthEngineConstants.SERVICE_ACCOUNT
        credentials = ee.ServiceAccountCredentials(
            service_account, 
            EarthEngineConstants.API_KEY_JSON
        )
        ee.Initialize(
            credentials, 
            project=EarthEngineConstants.PROJECT_NAME)
    
    def get_image_dates(
            self, 
            aoi_geojson:json, 
            start_date:str, 
            end_date:str
        ) -> Dict[str, any]:
        """
        Returns available images 
        """
        ee_polygon = self.get_aoi(aoi_geojson)
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        collection = ee.ImageCollection(
            self.sentinel_collection).filterDate(
                ee.Date(start_date), 
                ee.Date(end_date)
                ).filterBounds(ee_polygon)
        return collection.getInfo()