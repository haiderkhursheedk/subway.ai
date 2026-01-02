import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

import tensorflow as tf
import cv2
import numpy as np
import time
from adb_controller import ADBController
from utils.preprocess import preprocess_frame

class SubwaySurferAI:
    def __init__(self, model_path):
        """
        Initialize the AI agent
        
        Args:
            model_path: Path to the trained model
        """
        print(f"Loading model from: {model_path}")
        self.model = tf.keras.models.load_model(model_path)
        self.adb = ADBController()
        # Updated action map to include all actions
        self.action_map = {0: 'left', 1: 'right', 2: 'jump', 3: 'down', 4: 'running'}
        
    def process_screenshot(self, screenshot_path):
        """Process the screenshot for model input"""
        # Read and preprocess image
        frame = cv2.imread(str(screenshot_path))
        frame = preprocess_frame(frame)
        return np.expand_dims(frame, axis=0)
        
    def predict_action(self, frame):
        """Predict the next action"""
        prediction = self.model.predict(frame, verbose=0)
        action_idx = np.argmax(prediction[0])
        return self.action_map[action_idx]
        
    def run(self):
        """Run the AI agent"""
        try:
            # Start the game
            self.adb.start_game()
            time.sleep(5)  # Wait for game to load
            
            # Create temporary directory for screenshots
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            screenshot_path = temp_dir / "screenshot.png"
            
            while True:
                # Take screenshot
                self.adb.take_screenshot(screenshot_path)
                
                # Process screenshot and predict action
                frame = self.process_screenshot(screenshot_path)
                action = self.predict_action(frame)
                
                # Perform action
                self.adb.perform_action(action)
                
                # Small delay between actions
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nStopping AI agent...")
        finally:
            # Clean up
            self.adb.stop_game()
            if screenshot_path.exists():
                screenshot_path.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()

def main():
    # Convert string path to Path object
    model_path = Path("../model/model.h5")
    
    print(f"Looking for model at: {model_path.absolute()}")
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {model_path}")
        
    ai = SubwaySurferAI(str(model_path))  # Convert Path back to string for tf.keras.models.load_model
    ai.run()

if __name__ == "__main__":
    main() 