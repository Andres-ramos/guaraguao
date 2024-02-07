class CopernicusException(Exception):
    pass

class CopernicusManifestDownloadException(CopernicusException):
    pass

class CopernicusBandsDownloadException(CopernicusException):
    pass

class CopernicusAvaliableFilesException(CopernicusException):
    pass 

class CopernicusAuthenticationException(Exception):
    pass 