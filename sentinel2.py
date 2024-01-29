from earth_engine import earth_engine
import rioxarray as rxr
from io import BytesIO



class Sentinel2:

    def __init__(self):
        self.storage = ""
        self.data_downloader = earth_engine.EarthEngineAPI()


    def fetch_images(self, aoi, search_start, search_end, bands_list):
        return 

    def fetch_image(self, aoi, date, band_list):
        in_storage = False
        #TODO: Check storage
        if in_storage:
            #TODO: Implement
            image = self.storage.get()
            return 
        else :
            try :
                image_bytes = self.data_downloader.fetch_image_bytes(
                    aoi, date, band_list
                    )
      
                # image_id = self.storage.put(aoi, date, band_list, image_bytes)
                byte_stream = BytesIO(image_bytes)
                return rxr.open_rasterio(byte_stream)
            except Exception as e:
                raise e
