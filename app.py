# app.py
import streamlit as st
from video_processor import process_video
import os
import pandas as pd

# Function to save the uploaded file to the server's disk
def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join("temp", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return os.path.join("temp", uploaded_file.name)
    except Exception as e:
        # If there's any error saving the file, return None or handle it as you see fit
        st.error(f"Error saving file: {e}")
        return None

# Function to create a directory if it does not exist
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

st.title('Car Detection and Counting')
st.write('Upload an MP4 file to process.')

# Create a temporary directory to store uploaded files if it doesn't exist
ensure_dir("temp")

uploaded_file = st.file_uploader("Choose a file...", type="mp4")
if uploaded_file is not None:
    # Save the uploaded video file to disk
    video_path = save_uploaded_file(uploaded_file)
    
    if video_path:
        # Process the video (this part might take some time, depending on the video length and processing power)
        with st.spinner('Processing...'):
            process_video(video_path, "yolov8n.pt", "output_video.avi")
        
        # Show download link for new video
        with open("output_video.avi", "rb") as file:
            btn = st.download_button(
                label="Download Processed Video",
                data=file,
                file_name="output_video.avi",
                mime="video/avi"
            )
        
        # Show download link for the CSV file
        df_counts = pd.read_csv('object_count.csv')  # Assuming process_video saves the file to this path
        st.write(df_counts)
        csv = df_counts.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV file",
            data=csv,
            file_name='object_count.csv',
            mime='text/csv',
        )
