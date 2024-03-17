import streamlit as st
import json
import pandas as pd
import numpy as np
import folium
import ast


def load_gps_data(gps_file_path):
    df_gps = pd.read_csv(gps_file_path)
    df_gps['TimeDifference'] = (pd.to_datetime(df_gps['Timestamp'], utc=True) - pd.to_datetime(df_gps['Timestamp'].iloc[0], utc=True)).dt.total_seconds()
    df_gps.to_csv('Files/second_map_gps.csv')
    return df_gps

def closest_match(row, df_gps):
    differences = np.abs(df_gps['TimeDifference'] - row['timestamp'])
    min_difference_idx = np.argmin(differences)
    return df_gps['TimeDifference'].iloc[min_difference_idx]

def create_and_display_map(df_counts, df_gps):
    df_counts['ClosestMatch'] = df_counts.apply(lambda row: closest_match(row, df_gps), axis=1)
    df_merged = pd.merge(df_gps, df_counts, left_on="TimeDifference", right_on="ClosestMatch", how="right").drop_duplicates(subset=["timestamp"])
    df_merged = df_merged.groupby('object_count').first().reset_index()
    df_merged = df_merged[df_merged['object_count'] != 0]
    df_merged.to_csv('files/new_output.csv', index=False)
    
    
    df_gps['Coordinates'] = df_gps['Coordinates'].apply(ast.literal_eval)

# Initialize the map using the first location
    first_location = tuple(df_gps['Coordinates'].iloc[0])
    m = folium.Map(location=first_location, zoom_start=15)

    # Generate polyline coordinates by unpacking each pair of coordinates
    polyline_coordinates = [tuple(coord) for coord in df_gps['Coordinates']]
    folium.PolyLine(locations=polyline_coordinates, color='blue').add_to(m)

    # Plot markers for each row in df_merged
    for index, row in df_merged.iterrows():
        # Convert string to list if it's a string. This is just in case.
        coordinates = ast.literal_eval(row['Coordinates']) if isinstance(row['Coordinates'], str) else row['Coordinates']
        
        popup_content = f"Timestamp: {row['TimeDifference']:.2f}<br>Object Count: {row['object_count']}"
        folium.Marker(location=coordinates, popup=folium.Popup(popup_content, max_width=250)).add_to(m)

    # Assuming you have Streamlit to display the map
    folium_map = m._repr_html_()
    st.components.v1.html(folium_map, height=600, width=800)


