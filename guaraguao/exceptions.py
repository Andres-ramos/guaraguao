class Sentinel2Exception(Exception):
    pass

class Sentinel2AOIFormatException(Sentinel2Exception):
    pass

class Sentinel2StorageAPIException(Sentinel2Exception):
    pass 

class Sentinel2DataDownloaderException(Sentinel2Exception):
    pass 