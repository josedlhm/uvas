# video_processor.py
import streamlit as st
from ultralytics import YOLO
from ultralytics.solutions import object_counter
import cv2
import pandas as pd

def process_video(video_path, model_path="yolov8n.pt", output_video_name="output_video.avi"):
    """
    Process a video to count objects using YOLO and generate an output video and CSV with counts.

    Parameters:
    - video_path: Path to the input video file.
    - model_path: Path to the YOLO model file.
    - output_video_name: Name of the output annotated video file.
    """

    # Initialize YOLO model
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    # Define line points for counting
    center_top = (w // 2, 0)
    center_bottom = (w // 2, h)
    line_points = [center_top, center_bottom]

    # Define classes to count (e.g., cars)
    classes_to_count = [2]  # Adjust this based on your needs

    # Initialize video writer
    video_writer = cv2.VideoWriter(output_video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    # Initialize Object Counter
    counter = object_counter.ObjectCounter()
    counter.set_args(view_img=True, reg_pts=line_points, classes_names=model.names, draw_tracks=True)

    # Initialize a list to store data for each frame
    rows = []

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f'the numnber of frames is {total_frames}')

    # Initialize Streamlit progress bar
    progress_bar = st.progress(0)

    # Process each frame in the video
    frame_index = 0
    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            break

        # Detect and track objects using YOLO
        tracks = model.track(im0, persist=True, show=False, classes=classes_to_count)

        # Start counting objects
        counter.start_counting(im0, tracks)

        # Calculate timestamp based on frame index and frame rate
        timestamp = frame_index / fps

        # Append timestamp and object count to the list
        rows.append({"timestamp": timestamp, "object_count": counter.in_counts + counter.out_counts})

        # Write the annotated frame to the output video
        video_writer.write(im0)

        frame_index += 1

        if frame_index % 50 == 0:  
            progress_percentage = int(100 * frame_index / total_frames)
            progress_bar.progress(progress_percentage)

    # Release resources
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

    # Create DataFrame from the collected rows
    df_counts = pd.DataFrame(rows, columns=["timestamp", "object_count"])

    # Save DataFrame to CSV
    df_counts.to_csv('object_count.csv', index=False)

    print(f"Video processing complete. Results saved to {output_video_name} and object_count.csv.")

# If this file is run directly, prompt the user for a video file to process.
if __name__ == "__main__":
    video_path = input("Enter the path to the video file: ")
    process_video(video_path)
