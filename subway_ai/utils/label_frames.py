import cv2
import numpy as np
from pathlib import Path
import json
import os

class FrameLabeler:
    def __init__(self, frames_dir, output_dir):
        self.frames_dir = Path(frames_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.labels = {
            ord('a'): 'left',
            ord('d'): 'right',
            ord('w'): 'jump',
            ord('s'): 'down',
            ord('r'): 'running',
            ord('q'): 'quit'
        }
        self.current_frame = 0
        self.frames = []
        
        # Collect frames from all video directories
        for video_dir in self.frames_dir.glob("*"):
            if video_dir.is_dir():
                self.frames.extend(list(video_dir.glob("*.jpg")))
        
        self.frames = sorted(self.frames)
        print(f"Found {len(self.frames)} frames to label")
        
        # Load existing labels if any
        self.labels_file = self.output_dir / 'labels.json'
        if self.labels_file.exists():
            with open(self.labels_file, 'r') as f:
                self.labeled_data = json.load(f)
            print(f"Loaded {len(self.labeled_data)} existing labels")
            # Find the last labeled frame
            for i, frame in enumerate(self.frames):
                if frame.name not in self.labeled_data:
                    self.current_frame = i
                    break
        else:
            self.labeled_data = {}
        
    def label_frames(self):
        if not self.frames:
            print("No frames found to label!")
            return
            
        cv2.namedWindow('Frame Labeling', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Frame Labeling', self.mouse_callback)
        
        print("\nControls:")
        print("'a' - Label as left swipe")
        print("'d' - Label as right swipe")
        print("'w' - Label as jump")
        print("'s' - Label as down")
        print("'r' - Label as running (default state)")
        print("'q' - Save and quit")
        print("\nStarting from frame", self.current_frame)
        
        while self.current_frame < len(self.frames):
            frame_path = self.frames[self.current_frame]
            frame = cv2.imread(str(frame_path))
            
            if frame is None:
                print(f"Error reading frame: {frame_path}")
                self.current_frame += 1
                continue
            
            # Display frame number and path
            print(f"\rLabeling frame {self.current_frame + 1}/{len(self.frames)}: {frame_path.name}", end="")
            
            # Display frame
            cv2.imshow('Frame Labeling', frame)
            
            # Wait for key press
            key = cv2.waitKey(0)
            
            if key == ord('q'):
                break
            elif key in self.labels:
                # Save label
                self.labeled_data[frame_path.name] = self.labels[key]
                self.current_frame += 1
                
                # Save labels periodically
                if len(self.labeled_data) % 10 == 0:
                    self.save_labels()
        
        self.save_labels()
        cv2.destroyAllWindows()
        print(f"\nLabeled {len(self.labeled_data)} frames in total")
    
    def save_labels(self):
        with open(self.labels_file, 'w') as f:
            json.dump(self.labeled_data, f, indent=2)
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Left click to mark obstacles
            print(f"\nMarked obstacle at ({x}, {y})")

def main():
    # Get the script's directory
    script_dir = Path(__file__).parent.parent
    
    # Set up paths relative to the script directory
    frames_dir = script_dir / "data" / "frames"
    output_dir = script_dir / "data" / "labeled_frames"
    
    print(f"Looking for frames in: {frames_dir}")
    print(f"Saving labels to: {output_dir}")
    
    labeler = FrameLabeler(frames_dir, output_dir)
    labeler.label_frames()

if __name__ == "__main__":
    main() 