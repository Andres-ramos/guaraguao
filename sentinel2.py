from copernicus import copernicus
import pandas as pd
import rasterio 
import numpy as np
from pathlib import Path

class Sentinel:

    def __init__(self):
        # self.cache = cache.cache()
        self.data_downloader = copernicus.CopernicusClient('SENTINEL-2')


    def fetch_images(self, aoi, search_start, search_end, bands_list):
        return 

    def fetch_image(self, aoi, search_start, search_end, bands_list):
        cache_path = "./cache"
        avaliable_files_list = self.data_downloader.check_available_files(
            aoi=aoi, 
            search_period_start=search_start, 
            search_period_end=search_end)
        files_df = pd.DataFrame.from_dict(avaliable_files_list)

        product_name = files_df['Name'][1]
        product_id = files_df['Id'][1]
        unzipped_bands = self.data_downloader.download_files(
            product_identifier=product_id,
            product_name=product_name, 
            aoi=aoi,
            cache_path=cache_path,
            band_list=bands_list
            )

        band_np_arrays = []
        gain = 2
        for band in unzipped_bands:
            band = rasterio.open(Path(cache_path) / band, driver="JP2OpenJPEG")
            color = band.read(1)
            color_n = np.clip(color*gain/10000, 0, 1)
            band_np_arrays.append(color_n)
        
        composite = np.dstack(band_np_arrays)
        return composite
        


s = Sentinel()

aoi = "POLYGON ((-65.76543311765235 18.160414444432007, -65.77731192573422 18.15424297339561, -65.76560403575398 18.145228985891265, -65.7439828958638 18.157734753524366, -65.7527851781118 18.164555704063844, -65.76543311765235 18.160414444432007))"
search_period_start = "2023-05-01T00:00:00.000Z"
search_period_end = "2023-05-30T00:00:00.000Z"

image = s.fetch_image(aoi, search_period_start, search_period_end, ["B2", "B3", "B4", "B1", "B11"])
print(image)