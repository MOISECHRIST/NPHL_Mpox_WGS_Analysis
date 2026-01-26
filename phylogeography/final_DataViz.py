import pandas as pd
from Plot_migrations import plot_general_migration

import argparse
import sys

description = (
            "final_DataViz.py : "
            "This script allow user to vizualise the introductions found with AncestralChanges.py script."
        )

parser = argparse.ArgumentParser(description=description)
        
parser.add_argument("--migration", "-m", required=True, type=argparse.FileType('r'), help="Path to the AncestralChanges.py result csv file.\nFilewith columns : 'Origin', 'Destination','EventTime'")
parser.add_argument("--pointsGeoloc", "-p", required=True, type=argparse.FileType('r'), help="path to the csv file containing the geolication of each location in AncestralChanges.py result csv file. \nFile with columns : 'location', 'long', and 'lat'.")
parser.add_argument("--origins", "-o", nargs='+', help="Optional list of origin locations separated by white space to filter the plot (e.g., --origins South Center).")
parser.add_argument("--destinations", "-d", nargs='+', help="Optional list of destination locations separated by white space to filter the plot (e.g., --destinations Center North-West).")

args = parser.parse_args()

migration_file_path = args.migration
geoloc_file_path = args.pointsGeoloc
selected_origins = args.origins
selected_destinations = args.destinations

df_migration = pd.read_csv(migration_file_path)
location_geoloc=pd.read_csv(geoloc_file_path)

# Check for required columns
required_migration_cols = {'EventTime', 'Origin', 'Destination'}
if not required_migration_cols.issubset(df_migration.columns):
    missing = required_migration_cols - set(df_migration.columns)
    sys.exit(f"Error: Migration file is missing columns: {', '.join(missing)}")

required_geoloc_cols = {'location', 'long', 'lat'}
if not required_geoloc_cols.issubset(location_geoloc.columns):
    missing = required_geoloc_cols - set(location_geoloc.columns)
    sys.exit(f"Error: Geolocation file is missing columns: {', '.join(missing)}")

def map_locations(location, locations_set=location_geoloc,long=True):
    if location in pd.unique(locations_set["location"]):
        if long:
            return float(locations_set[locations_set["location"]==location]["long"])
        else :
            return float(locations_set[locations_set["location"]==location]["lat"])
    else : 
        return None 

df_migration["Origin_long"]=df_migration["Origin"].map(lambda x : map_locations(x))
df_migration["Origin_lat"]=df_migration["Origin"].map(lambda x : map_locations(x, long=False))

df_migration["Destination_long"]=df_migration["Destination"].map(lambda x : map_locations(x))
df_migration["Destination_lat"]=df_migration["Destination"].map(lambda x : map_locations(x, long=False))

df_migration_clean = df_migration[df_migration["Origin"]!='UNKNOWN']
df_migration_clean = df_migration_clean[df_migration_clean["Destination"]!='UNKNOWN']

plot_general_migration(location_geoloc, df_migration_clean, origins=selected_origins, destinations=selected_destinations)