To run the package install the spatialite mod
```
  apt-get install libsqlite3-mod-spatialite
```

Create the ee_api_key file that you can get after creating an account on google earth engine.
```
 touch ee_api_key.json
```

Create a copernicus account, get a username and password. Create an env file inside the copernicus folder
paste the contents into the file 

```
username=user
password=password
```
TODO: 
1. Add band_list as an optional parameter and as a default put all the bands
2. Change naming scheme! Right now packge is called Satellite-API which can't be imported into python because of the "-"
3. Add wrapper to the available_files method to simply return the date of the available picture
4. Add better documentation. Particularly how to get the earth engine stuff and the copernicus stuff. 
5. Fix earth engine constants file! It needs to be modified in order to get the earth engine credentials
