#!/usr/bin/env python3

import requests
import pandas as pd
import os
import time
import json

NCDOT_INCIDENTS_FILE = "https://tims.ncdot.gov/TIMS/Excel.aspx"
TMP_PATH = "tmp/ncdot_incidents.xls"
OUT_PATH = "out/nc_roadclosures.geojson"

# Thanks Geoff Boeing, https://geoffboeing.com/2015/10/exporting-python-data-geojson/
def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    geojson = {'type':'FeatureCollection', 'features':[]}
    for _, row in df.iterrows():
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}
        feature['geometry']['coordinates'] = [row[lon],row[lat]]
        for prop in properties:
            feature['properties'][prop] = row[prop]
        geojson['features'].append(feature)
    return geojson


if not (os.path.exists(TMP_PATH) and (time.time() - os.path.getmtime(TMP_PATH)) < 3600):
	print("getting incidents file")
	response = requests.get(NCDOT_INCIDENTS_FILE, stream=True)
	response.raise_for_status()
	with open(TMP_PATH, 'wb') as fh:
		for block in response.iter_content(1024):
			fh.write(block)

xl = pd.ExcelFile(TMP_PATH)
df = xl.parse(xl.sheet_names[0])
df_filtered = df.loc[
		(df['IncidentTypeDesc'] == "Weather Event") &
		(df["Condition"] == "Road Closed")]

out = df_to_geojson(
		df_filtered,
		lat="Latitude",
		lon="Longitude",
		properties=["RoadName", "Direction", "Reason"]
)

with open(OUT_PATH, 'w') as fh:
	fh.write(json.dumps(out))

print("done. {} records retrieved and saved.".format(df_filtered.shape[0]))