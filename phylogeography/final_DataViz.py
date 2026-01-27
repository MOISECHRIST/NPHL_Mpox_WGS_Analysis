import pandas as pd
from Plot_migrations import plot_general_migration
from dash import Dash, dcc, html, Input, Output

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
parser.add_argument("--savepdf", "-s", action="store_true", help="Save plot in pdf file")

args = parser.parse_args()

migration_file_path = args.migration
geoloc_file_path = args.pointsGeoloc
selected_origins = args.origins
selected_destinations = args.destinations
savepdf=args.savepdf

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
            return float(locations_set[locations_set["location"]==location]["long"].astype(float))
        else :
            return float(locations_set[locations_set["location"]==location]["lat"].astype(float))
    else : 
        return None 

df_migration["Origin_long"]=df_migration["Origin"].map(lambda x : map_locations(x))
df_migration["Origin_lat"]=df_migration["Origin"].map(lambda x : map_locations(x, long=False))

df_migration["Destination_long"]=df_migration["Destination"].map(lambda x : map_locations(x))
df_migration["Destination_lat"]=df_migration["Destination"].map(lambda x : map_locations(x, long=False))

df_migration_clean = df_migration[df_migration["Origin"]!='UNKNOWN']
df_migration_clean = df_migration_clean[df_migration_clean["Destination"]!='UNKNOWN']

all_destinations = pd.unique(df_migration_clean["Destination"])
all_origins = pd.unique(df_migration_clean["Origin"])

all_destinations = list(pd.unique(df_migration_clean["Destination"]))
all_origins = list(pd.unique(df_migration_clean["Origin"]))

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Interactive Migration Map", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("Origin locations :"),
        dcc.Dropdown(
            options=all_origins,
            value=all_origins, # Par défaut, tout est sélectionné
            id='selected_origins',
            multi=True
        ),
    ], style={'padding': 5}),

    html.Div([
        html.Label("Destination locations :"),
        dcc.Dropdown(
            options=all_destinations,
            value=all_destinations,
            id="selected_destinations",
            multi=True
        ),
    ], style={'padding': 10}),

    dcc.Graph(id="graph", style={'height': '800px'})
])

@app.callback(
    Output("graph", "figure"),
    Input("selected_origins", "value"),
    Input("selected_destinations", "value")
)
def update_chart(origins_list, destinations_list):
    if not origins_list or not destinations_list:
        return {} 

    fig = plot_general_migration(
        location_geoloc, 
        df_migration_clean, 
        origins=origins_list, 
        destinations=destinations_list,
        save=savepdf
    )
    return fig

app.run()