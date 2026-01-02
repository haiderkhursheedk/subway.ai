import cv2
import numpy as np
from pathlib import Path
import time
from datetime import datetime
from adb_controller import ADBController
import subprocess

class DataGatherer:
    def __init__(self):
        self.adb = ADBController()
        self.base_dir = Path("data/gameplay_images")
        self.actions = ['down', 'left', 'running', 'right', 'up']
        
        # Create directories for each action
        for action in self.actions:
            (self.base_dir / action).mkdir(parents=True, exist_ok=True)
            
        # Create temp directory for screenshots
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        
    def monitor_touch_events(self):
        """Monitor touch events from ADB"""
        # Use ADB to monitor touch events
        process = subprocess.Popen(
            [self.adb.adb_path, 'shell', 'getevent', '-l'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process

    def parse_touch_event(self, line):
        """Parse touch event to determine action"""
        # Example line parsing for touch events
        # You might need to adjust these coordinates based on your device
        if 'ABS_MT_POSITION_X' in line:
            x_pos = int(line.split('ABS_MT_POSITION_X')[-1].strip(), 16)
            if x_pos < self.screen_width / 3:
                return 'left'
            elif x_pos > (2 * self.screen_width) / 3:
                return 'right'
        elif 'ABS_MT_POSITION_Y' in line:
            y_pos = int(line.split('ABS_MT_POSITION_Y')[-1].strip(), 16)
            if y_pos < self.screen_height / 3:
                return 'up'
            elif y_pos > (2 * self.screen_height) / 3:
                return 'down'
        return None

    def gather_data(self):
        print("Starting data gathering...")
        print("\nPlay Subway Surfers normally on your phone.")
        print("The script will automatically capture your actions.")
        print("Press Ctrl+C to stop gathering data.\n")
        
        screenshot_path = self.temp_dir / "current_screenshot.png"
        
        # Get screen dimensions from ADB
        screen_info = subprocess.check_output([self.adb.adb_path, 'shell', 'wm', 'size'])
        screen_info = screen_info.decode().strip()
        self.screen_width, self.screen_height = map(int, screen_info.split()[-1].split('x'))
        
        # Start monitoring touch events
        touch_process = self.monitor_touch_events()
        last_action = 'running'
        last_action_time = time.time()
        
        try:
            while True:
                # Take screenshot
                self.adb.take_screenshot(screenshot_path)
                
                # Read and process touch events
                while touch_process.stdout.readable():
                    line = touch_process.stdout.readline()
                    if not line:
                        break
                        
                    action = self.parse_touch_event(line)
                    if action:
                        last_action = action
                        last_action_time = time.time()
                
                # If no action for 0.5 seconds, consider it running
                if time.time() - last_action_time > 0.5:
                    last_action = 'running'
                
                # Save frame with timestamp and current action
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                save_path = self.base_dir / last_action / f"frame_{timestamp}.jpg"
                
                # Read and save the screenshot
                frame = cv2.imread(str(screenshot_path))
                if frame is not None:
                    cv2.imwrite(str(save_path), frame)
                    print(f"\rSaved frame as {last_action}", end="")
                
                # Small delay to prevent too many screenshots
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\nStopping data gathering...")
        finally:
            # Clean up
            touch_process.terminate()
            if screenshot_path.exists():
                screenshot_path.unlink()
            if self.temp_dir.exists():
                self.temp_dir.rmdir()
            
            # Print statistics
            print("\n\nData gathering completed!")
            for action in self.actions:
                count = len(list((self.base_dir / action).glob("*.jpg")))
                print(f"{action}: {count} frames")

def main():
    gatherer = DataGatherer()
    gatherer.gather_data()

if __name__ == "__main__":
    main() 