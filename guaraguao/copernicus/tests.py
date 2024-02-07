import unittest
from copernicus import CopernicusClient

class CopernicusClientTest(unittest.TestCase):

    # def test_check_avaliable_files(self):
    #     name = "SENTINEL-2"
    #     c = CopernicusClient(name)

    #     aoi = "POLYGON ((-65.76543311765235 18.160414444432007, -65.77731192573422 18.15424297339561, -65.76560403575398 18.145228985891265, -65.7439828958638 18.157734753524366, -65.7527851781118 18.164555704063844, -65.76543311765235 18.160414444432007))"
    #     search_period_start = "2023-05-01T00:00:00.000Z"
    #     search_period_end = "2023-05-30T00:00:00.000Z"
    #     file_list = c.check_available_files(aoi, search_period_start, search_period_end)
    #     result = {'@odata.mediaContentType': 'application/octet-stream', 'Id': '412c606f-5b0b-4a39-97b8-95d466475bc3', 'Name': 'S2A_MSIL1C_20230517T150721_N0509_R082_T19QHA_20230517T200719.SAFE', 'ContentType': 'application/octet-stream', 'ContentLength': 810788320, 'OriginDate': '2023-05-17T21:58:50.948Z', 'PublicationDate': '2023-05-17T22:05:23.128Z', 'ModificationDate': '2023-05-17T22:05:23.128Z', 'Online': True, 'EvictionDate': '', 'S3Path': '/eodata/Sentinel-2/MSI/L1C/2023/05/17/S2A_MSIL1C_20230517T150721_N0509_R082_T19QHA_20230517T200719.SAFE', 'Checksum': [{}], 'ContentDate': {'Start': '2023-05-17T15:07:21.024Z', 'End': '2023-05-17T15:07:21.024Z'}, 'Footprint': "geography'SRID=4326;POLYGON ((-65.11838 18.5832839305928, -65.11011 18.9516480987629, -66.151276 18.9705988855996, -66.1676 17.9794315245556, -65.27008 17.9639183478561, -65.24832 18.0529917293503, -65.21207 18.2014600604752, -65.17572 18.3498188031194, -65.13934 18.4980945714561, -65.11838 18.5832839305928))'", 'GeoFootprint': {'type': 'Polygon', 'coordinates': [[[-65.11838, 18.5832839305928], [-65.11011, 18.9516480987629], [-66.151276, 18.9705988855996], [-66.1676, 17.9794315245556], [-65.27008, 17.9639183478561], [-65.24832, 18.0529917293503], [-65.21207, 18.2014600604752], [-65.17572, 18.3498188031194], [-65.13934, 18.4980945714561], [-65.11838, 18.5832839305928]]]}}
    #     self.assertEqual(file_list[0], result, 'Test Passed!')

    def test_user_authentication(self):
        name = "SENTINEL-2"
        c = CopernicusClient(name)
        response = c.authenticate_user()
        if 'access_token' in response.keys():
            self.assertEqual(1, 1, 'user authentication test passsed')
        else :
            self.assertEqual(1, 2, 'user authentication test failed')



    def test_download_manifest(self):
        return 
    
    def test_get_band_locations(self):
        return 
    
    def test_download_bands(self):
        return 

if __name__ == '__main__':
    unittest.main()