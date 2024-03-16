import streamlit as st
import json
import pandas as pd
import numpy as np
import folium

def load_gps_data(gps_file_path):
    with open(gps_file_path) as file:
        data = json.load(file)
    timestamps_gps = [entry['date'] for entry in data['1']['streams']['GPS5']['samples']]
    coordinates_list = [entry['value'] for entry in data['1']['streams']['GPS5']['samples']]
    df_gps = pd.DataFrame({'Timestamp': timestamps_gps, 'Coordinates': coordinates_list})
    df_gps['TimeDifference'] = (pd.to_datetime(df_gps['Timestamp'], utc=True) - pd.to_datetime(df_gps['Timestamp'].iloc[0], utc=True)).dt.total_seconds()
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
    df_merged.to_csv('files/old_output.csv', index=False)
    
    m = folium.Map(location=df_gps['Coordinates'].iloc[0][:2], zoom_start=15)
    polyline_coordinates = [(coord[0], coord[1]) for coord in df_gps['Coordinates']]
    folium.PolyLine(locations=polyline_coordinates, color='blue').add_to(m)
    for index, row in df_merged.iterrows():
        popup_content = f"Timestamp: {row['TimeDifference']:.2f}<br>Object Count: {row['object_count']}"
        folium.Marker(location=(row['Coordinates'][0], row['Coordinates'][1]), popup=folium.Popup(popup_content)).add_to(m)
    
    # Streamlit components to display HTML
    folium_map = m._repr_html_()
    st.components.v1.html(folium_map, height=600, width=800)
