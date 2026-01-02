import cv2
import os
from pathlib import Path
import numpy as np

def extract_frames(video_path, output_dir, frame_interval=5):
    """
    Extract frames from video at specified intervals
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save frames
        frame_interval: Extract every nth frame
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Open video file
    cap = cv2.VideoCapture(str(video_path))
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    frame_count = 0
    frame_number = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            # Save frame
            frame_path = os.path.join(output_dir, f"frame_{frame_number:06d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_number += 1
            
        frame_count += 1
    
    cap.release()
    print(f"Extracted {frame_number} frames from {video_path}")

def process_all_videos(video_dir, output_dir):
    """
    Process all videos in the directory
    """
    video_dir = Path(video_dir)
    for video_file in video_dir.glob("*.mp4"):
        print(f"Processing {video_file}")
        video_output_dir = Path(output_dir) / video_file.stem
        extract_frames(video_file, video_output_dir)

if __name__ == "__main__":
    # Get the script's directory
    script_dir = Path(__file__).parent.parent
    
    # Set up paths relative to the script directory
    video_dir = script_dir / "data" / "raw_videos"
    output_dir = script_dir / "data" / "frames"
    
    print(f"Processing videos from: {video_dir}")
    print(f"Saving frames to: {output_dir}")
    
    process_all_videos(video_dir, output_dir) 