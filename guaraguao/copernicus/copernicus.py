import requests
from requests import RequestException
from pathlib import Path
import xml.etree.ElementTree as ET
import json
import rasterio 
from rasterio.windows import Window
from decouple import config

from .exceptions import CopernicusBandsDownloadException, CopernicusAuthenticationException, CopernicusAvaliableFilesException, CopernicusManifestDownloadException

from shapely.geometry import shape 
import shapely 

from typing import Dict
from typing_json import json

#TODO: Make a query builder class to abstract the nonsense
#TODO: Add constants file

class CopernicusClient:

    def __init__(self, collection_name):
        self.catalogue_odata_url = "https://catalogue.dataspace.copernicus.eu/odata/v1"
        self.collection_name = collection_name
        #TODO: Eventually this needs to me modularized
        #TODO: Figure out what other product types there are
        self.product_type = "S2MSI1C"
        self.session = self.get_session()

    ###################################################################################
    # Main Methods
    ###################################################################################

    #Method to check available files in copernicus enviroment
    def check_available_files(
            self, 
            aoi: json, 
            search_period_start: str, 
            search_period_end: str
        )-> Dict[str, any]:
        '''Method that checks the avaliable data files in the copernicus enviroment

        Parameters:
        aoi (shapely polygon as a string) - geojson
        search_period_start (date) - start date of searching period
        search_period_end (date) - end date of searching period

        Returns:
        list- each entry is a dict with information related to file
        '''
        aoi_in_wkt = shapely.to_wkt(shape(aoi["features"][0]["geometry"]))
        search_query = f"{self.catalogue_odata_url}/Products?$filter=Collection/Name eq '{self.collection_name}' and Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq '{self.product_type}') and OData.CSC.Intersects(area=geography'SRID=4326;{aoi_in_wkt}') and ContentDate/Start gt {search_period_start} and ContentDate/Start lt {search_period_end}"
        try :
            response = self.session.get(search_query).json()
            return response['value']
        except RequestException as e:
            raise CopernicusAvaliableFilesException from e
        
    #Main method in this class
    #Downloads the files
    def download_files(self, product_identifier, product_name, aoi, cache_path, band_list):
        '''Main method of the module. Downloads satellite image files

        Parameters:
        product_identifier (string)
        product_name (string)
        

        Returns:
        unzipped_bands - list with file name of each unzipped band
        '''
        #TODO: Add check for band list
        #Downloads the manifest file
        print("downloading manifest")
        manifest_path = self.download_manifest(product_identifier, product_name, cache_path)
        #Finds band locations in the manifest
        # print("Getting band locations")
        band_location = self.get_band_locations(product_name, manifest_path, band_list)
        # #Downloads the zipped file for each band
        bands = self.download_bands(band_location=band_location, 
                            product_identifier=product_identifier, 
                            product_name=product_name, band_path=cache_path)
        # #Unzips a subset of each zipped band file
        # bands = ["70d9a266-b69e-43a4-91d9-9b8daee0ec4e-T19QHA_20230502T150719_B04.jp2",
        #          "70d9a266-b69e-43a4-91d9-9b8daee0ec4e-T19QHA_20230502T150719_B02.jp2",
        #          "70d9a266-b69e-43a4-91d9-9b8daee0ec4e-T19QHA_20230502T150719_B03.jp2"]
        # print(f"unzipping bands {bands}")
        unzipped_bands = self.unzip_bands(
            bands=bands, 
            aoi=aoi, 
            cache_path=cache_path, 
            uz_band_path=cache_path, 
            product_id=product_identifier)
        
        return unzipped_bands
    

    #################################################################################
    #Helper methods
    ##################################################################################

    def download_manifest(self, product_identifier, product_name, manifest_path):
        '''
        Downloads manifest file corresponding to a given file

        Parameters:
        product_identifier (string)
        product_name (string)
        manifest_path (string) - path to store the manifest

        Returns:
        manifest file (string) - path to manifest.xml file 
        '''
        url = f"{self.catalogue_odata_url}/Products({product_identifier})/Nodes({product_name})/Nodes(MTD_MSIL1C.xml)/$value"   
        #Waits for connection
        response = self.session.get(url, allow_redirects=False)
        while response.status_code in (301, 302, 303, 307):
            url = response.headers["Location"]
            response = self.session.get(url, allow_redirects=False)

        #Fetches the manifest file once connection established
        try :
            file = self.session.get(url, verify=False, allow_redirects=True)

            outfile = Path(manifest_path) / f"{product_identifier}-MTD_MSIL1C.xml"
            outfile.write_bytes(file.content)
            return outfile

        except RequestException as e:
            raise CopernicusManifestDownloadException from e
        

    def get_band_locations(self, product_name, outfile, band_list):
        '''
        Finds the band locations in the manifest

        Parameters:
        product_name (string) - product name
        outfile (?) - ??
        band_list (list) - list with band strings

        returns:
        band_locations (list) - list with each band path
        '''
       
        tree = ET.parse(str(outfile))
        # get the parent tag
        root = tree.getroot()
        # Get the location of individual bands in Sentinel-2 granule
        band_location = []
        for band in band_list:
            band_index = self.map_band_to_index(band)
            band_location.append(f"{product_name}/{root[0][0][12][0][0][band_index].text}.jp2".split("/"))

        return band_location
    
    def download_bands(self, band_location, product_identifier, product_name, band_path):
        '''
        Downloads the zipped files for each band

        Parameters:
        band_location (list) - list of bands
        product_identifier (string) - 
        product_name (string) - 
        band_path (string) - string with path for bands download

        Returns:
        bands (list) - string list with each band path
        '''
        bands = []
        for band_file in band_location:
            #Waits for the connection
            url = f"{self.catalogue_odata_url}/Products({product_identifier})/Nodes({product_name})/Nodes({band_file[1]})/Nodes({band_file[2]})/Nodes({band_file[3]})/Nodes({band_file[4]})/$value"
            response = self.session.get(url, allow_redirects=False)
            while response.status_code in (301, 302, 303, 307):
                print("Pending Download Connection")
                url = response.headers["Location"]
                response = self.session.get(url, allow_redirects=False)
            
            #Tries to download the file once its connected
            try :
                print("Downloading")
                file = self.session.get(url, verify=False, allow_redirects=True)

                outfile = Path(band_path) / f"{product_identifier}-{band_file[4]}"
                outfile.write_bytes(file.content)
                bands.append(str(outfile))
                
            except RequestException as e:
                raise CopernicusBandsDownloadException from e

        return bands
    

    def unzip_bands(self, bands, aoi, cache_path, uz_band_path, product_id):

        #TODO: Modularize this
        xsize, ysize = 10980/2 , 10980/2
        xoff, yoff, xmax, ymax = 0, 0, 0, 0
        unzipped_bands = []
        for band_file in bands:
            # Reads the zipped jp2 filezipped
            band_number = self.get_band_number(band_file)
            #TODO: Add the crs to the opening of the file
            full_band = rasterio.open(f"{cache_path}/{band_file}", driver="JP2OpenJPEG")
            if xmax == 0:
                xmin, xmax = 0, full_band.width - xsize
            if ymax == 0:
                ymin, ymax = 0, full_band.height - ysize
            # if xoff == 0:
            #     xoff, yoff = 1000, 1000

            window = Window(xoff, yoff, xsize, ysize)
            transform = full_band.window_transform(window)
            profile = full_band.profile
            crs = full_band.crs
            profile.update({"height": xsize, "width": ysize, "transform": transform})

            file_name = f"unzipped-{product_id}-patch_band_{band_number}.jp2"
            with rasterio.open(
                Path(uz_band_path) / file_name, "w", **profile
            ) as patch_band:
                # Read the data from the window and write it to the output raster
                patch_band.write(full_band.read(window=window))

            unzipped_bands.append(file_name)

        return unzipped_bands
    
    def get_band_number(self, band):
        '''
        Helper method that gets band number from band file
        '''
        s = band.split("_")[-1]
        d = s.split(".")[0]
        num_str = d.split("B")[1]
        
        if num_str[0] == "0":
            return int(num_str[1])
    
        return int(num_str)

    def map_band_to_index(self, band):
        '''
        Helper method that maps band to index in manifest
        '''
        band_dict = {
            "B1": 0,
            "B2": 1,
            "B3": 2,
            "B4": 3,
            "B5": 4,
            "B6": 5,
            "B7": 6,
            "B8": 7,
            "B8A": 8,
            "B9": 9,
            "B10": 10,
            "B11": 11,
            "B12": 12
        }
        return band_dict[band]
    #########################################################################
    #Authentication stuff:
    #########################################################################

    def get_session(self):
        authentication_response = self.authenticate_user()
        access_token = authentication_response['access_token']
        session = requests.Session()
        session.headers["Authorization"] = f"Bearer {access_token}"
        return session

    def authenticate_user(self):
        username = config("username")
        password = config("password")
        auth_server_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        data = {
            "client_id": "cdse-public",
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        try :
            
            response = requests.post(auth_server_url, data=data, verify=True, allow_redirects=False)
            return json.loads(response.text)
        
        except RequestException as e:
            raise CopernicusAuthenticationException from e
    
    


# import pandas as pd
# name = "SENTINEL-2"
# c = CopernicusClient(name)

# aoi = "POLYGON ((-65.76543311765235 18.160414444432007, -65.77731192573422 18.15424297339561, -65.76560403575398 18.145228985891265, -65.7439828958638 18.157734753524366, -65.7527851781118 18.164555704063844, -65.76543311765235 18.160414444432007))"
# search_period_start = "2023-05-01T00:00:00.000Z"
# search_period_end = "2023-05-30T00:00:00.000Z"
# dict = c.check_available_files(aoi, search_period_start, search_period_end)
# # print(dict[0].keys())
# # result = pd.DataFrame.from_dict(dict)

# # print(result)
# i = 0
# product_identifier = dict[0]['Id']
# product_name = dict[0]['Name']
# # print(product_identifier)
# # print(product_name)

# c.download_files(product_name=product_name, product_identifier=product_identifier)