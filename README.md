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

1. Quality of life
    1.b Improve aoi input to include polygon instead of just feature collection
    1.d Add better documentation. Particularly how to get the earth engine stuff and the copernicus stuff.
    1.e Add metadata to xarray dataset
2. Features
    2.b Add feature to export data in nice format

3. Add example of usage to documentation :)
