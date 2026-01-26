import plotly.graph_objects as go
import plotly.colors as pc
import pandas as pd
import numpy as np

def get_bezier_curve(lon1, lat1, lon2, lat2, curvature=0.2, num_points=30):
    """
    Calculates the coordinates of a quadratic Bezier curve between two points.

    Args:
        lon1 (float): Longitude of the starting point.
        lat1 (float): Latitude of the starting point.
        lon2 (float): Longitude of the ending point.
        lat2 (float): Latitude of the ending point.
        curvature (float, optional): The curvature factor of the path. Defaults to 0.2.
        num_points (int, optional): The number of points to generate for the curve. Defaults to 30.

    Returns:
        tuple: Two numpy arrays containing the longitudes and latitudes of the curve points.
    """
    mid_lon = (lon1 + lon2) / 2
    mid_lat = (lat1 + lat2) / 2

    dist = ((lon2 - lon1)**2 + (lat2 - lat1)**2)**0.5
    
    ctrl_lon = mid_lon - (lat2 - lat1) * curvature 
    ctrl_lat = mid_lat + (lon2 - lon1) * curvature + (dist * curvature)

    t = np.linspace(0, 1, num_points)
    
    curve_lon = (1-t)**2 * lon1 + 2*(1-t)*t * ctrl_lon + t**2 * lon2
    curve_lat = (1-t)**2 * lat1 + 2*(1-t)*t * ctrl_lat + t**2 * lat2
    
    return curve_lon, curve_lat

def plot_general_migration(locations_data, migration_data, origins=None, destinations=None, save=True):
    """
    Generates and saves a geographical plot of migration paths.

    Args:
        locations_data (pd.DataFrame): DataFrame containing 'location', 'long', and 'lat' columns.
        migration_data (pd.DataFrame): DataFrame containing migration events with 'Origin', 'Destination', 
                                       'EventTime', and coordinate columns.
        origins (str or list, optional): Filter for origin locations. Defaults to None.
        destinations (str or list, optional): Filter for destination locations. Defaults to None.

    Returns:
        None: Displays the plot and saves it as a PDF.
    """
    
    target_data = migration_data.copy()
    
    if origins:
        if isinstance(origins, str): 
            origins = [origins]
        target_data = target_data[target_data['Origin'].isin(origins)]
        
    if destinations:
        if isinstance(destinations, str): 
            destinations = [destinations]
        target_data = target_data[target_data['Destination'].isin(destinations)]

    if target_data.empty:
        print("Aucune migration trouvée avec ces critères.")
        return

    fig = go.Figure()
    
    fig.add_trace(go.Scattergeo(
        lon = locations_data['long'],
        lat = locations_data['lat'],
        hoverinfo = 'text',
        text = locations_data['location'],
        mode = 'markers',
        marker = dict(
            size = 6,  
            color = 'rgb(255, 0, 0)',
            line = dict(width = 1, color = 'rgba(68, 68, 68, 0)')
        )
    ))

    min_year = int(migration_data['EventTime'].min())
    max_year = int(migration_data['EventTime'].max())
    time_span = max_year - min_year
    if time_span == 0: time_span = 1
    palette = 'Viridis' 

    for i in target_data.index:
        current_time = target_data['EventTime'][i]
        current_year_integer = int(current_time)
        
        orig_name = target_data['Origin'][i]
        dest_name = target_data['Destination'][i]
        
        lon_start = target_data['Origin_long'][i]
        lat_start = target_data['Origin_lat'][i]
        lon_end = target_data['Destination_long'][i]
        lat_end = target_data['Destination_lat'][i]

        lons_curve, lats_curve = get_bezier_curve(lon_start, lat_start, lon_end, lat_end)

        normalized_val = (current_year_integer - min_year) / time_span
        line_color = pc.sample_colorscale(palette, [normalized_val])[0]
        
        tooltip_text = (
            f"<b>Origine :</b> {orig_name}<br>"
            f"<b>Destination :</b> {dest_name}<br>"
            f"<b>Date :</b> {current_time:.2f}"
        )
        
        fig.add_trace(
            go.Scattergeo(
                lon = lons_curve,
                lat = lats_curve,
                mode = 'lines',
                line = dict(
                    width = 2,
                    color = line_color 
                ),
                opacity = float(target_data['EventTime'][i])/float(target_data['EventTime'].max()), 
                hoverinfo = 'text',    
                text = tooltip_text,   
                showlegend = False 
            )
        )

    fig.add_trace(go.Scattergeo(
        lon=[None], lat=[None],
        mode='markers',
        marker=dict(
            colorscale=palette,
            cmin=min_year,
            cmax=max_year,
            colorbar=dict(
                orientation='h',
                y=-0.01,
                x=0.5,
                xanchor='center',    
                yanchor='top', 
                len=0.6,             
                thickness=15,        
                title_side='top',
                title="Year", 
                tickmode="array", 
                tickvals=list(range(min_year, max_year + 1)), 
                ticktext=list(range(min_year, max_year + 1))
            )
        )
    ))

    title_parts = ["Outbreak Introduction"]
    if origins:
        title_parts.append(f"FROM {', '.join(origins)}")
    else:
        title_parts.append("FROM All")
        
    if destinations:
        title_parts.append(f"TO {', '.join(destinations)}")
    else:
        title_parts.append("TO All")

    full_title = " ".join(title_parts)

    fig.update_layout(
        title_text = full_title,
        height = 800, 
        margin = dict(l=0, r=0, t=40, b=0),
        geo = dict(
            scope = 'world',
            resolution = 50, 
            showcountries = True,
            countrycolor = "rgb(150, 150, 150)",
            showland = True,
            landcolor = "rgb(240, 240, 240)",
            showocean = True,
            oceancolor = "rgb(200, 225, 255)", 
            showframe = False,
            showcoastlines = True,
        )
    )

    if save:
        filename_parts = ["Migration_Map"]
        if origins:
            filename_parts.append(f"From_{'-'.join(origins)}")
        if destinations:
            filename_parts.append(f"To_{'-'.join(destinations)}")
        
        safe_filename = "_".join(filename_parts) + ".pdf"
        
        print(f"Output file path : {safe_filename}")
        fig.write_image(safe_filename, width=1200, height=800)
    
    fig.show()