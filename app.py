import streamlit as st
from video_processor import process_video
from map import load_gps_data, create_and_display_map
from make_chart import plot_object_count
from process_data import create_historical_data
from get_coordinates import generate_coordinates
import os
import pandas as pd

def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join("temp", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return os.path.join("temp", uploaded_file.name)
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

st.title('Car Detection and Counting Dashboard')
st.markdown("""
Upload an MP4 file to process and analyze car counts and locations over time. 
After processing, explore dynamic visualizations of detected vehicles, including trends and geographical data.
""")

ensure_dir("temp")

generate_coordinates('files/sample_output.gpx', 'files/sample_output.csv')

uploaded_file = st.file_uploader("Choose a file...", type="mp4")
if uploaded_file is not None:
    if 'processed' not in st.session_state or st.session_state.video_path != uploaded_file.name:
        st.session_state.processed = False
        st.session_state.video_path = uploaded_file.name

    if not st.session_state.processed:
        video_path = save_uploaded_file(uploaded_file)
        if video_path:
            with st.spinner('Processing...'):
                process_video(video_path, "yolov8n.pt", "output_video.avi")
            st.session_state.processed = True

    if st.session_state.processed:
        st.success("Video processed successfully!")
        st.write("## Key Metrics")
        col1, col2 = st.columns(2)
        with col1:
            historical_data = create_historical_data('object_count.csv', 'historical_data.csv')
            total_cars_detected = historical_data['object_count'].iloc[-1]
            st.metric(label="Total Cars Detected in Last Video", value=total_cars_detected)
        with col2:
            if len(historical_data) > 1:
                total_change = historical_data['object_count'].iloc[-1] - historical_data['object_count'].iloc[-2]
                st.metric(label="Change from Previous Submission", value=total_change)
            else:
                st.metric(label="Change from Previous Submission", value="N/A")
        
        st.write("## Historical Data Analysis")
        fig = plot_object_count(historical_data)
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("## Improved Geographical Distribution of Detected Cars")
        df_counts = pd.read_csv('object_count.csv')
        df_gps = load_gps_data('files/sample_output.csv')
        create_and_display_map(df_counts, df_gps)

        with st.expander("Download Processed Results"):
            with open("output_video.avi", "rb") as file:
                st.download_button(
                    label="Download Processed Video",
                    data=file,
                    file_name="output_video.avi",
                    mime="video/avi"
                )
            
            csv = df_counts.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV Data",
                data=csv,
                file_name='object_count.csv',
                mime='text/csv',
            )
