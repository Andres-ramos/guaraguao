CREATE TABLE IF NOT EXISTS SatelliteImage (
  id INTEGER PRIMARY KEY,
  aoi GEOMETRY NOT NULL,
  date TEXT NOT NULL, 
  file_path TEXT NOT NULL,
  band_list TEXT NOT NULL,
  collection TEXT NOT NULL,
  satellite TEXT NOT NULL,
  metadata TEXT NOT NULL
);