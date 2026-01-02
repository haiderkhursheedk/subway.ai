import subprocess
import time
from pathlib import Path
import os

class ADBController:
    def __init__(self):
        # Try to find ADB from Android Studio installation
        self.adb_path = self._find_adb_path()
        self.check_adb_connection()
        
    def _find_adb_path(self):
        """Find ADB executable from Android Studio installation"""
        # Common locations for Android SDK
        possible_locations = [
            # Windows - Android Studio default location
            Path(os.environ.get('LOCALAPPDATA', '')) / "Android" / "Sdk" / "platform-tools" / "adb.exe",
            # Windows - User home directory
            Path.home() / "AppData" / "Local" / "Android" / "Sdk" / "platform-tools" / "adb.exe",
        ]
        
        for path in possible_locations:
            if path.exists():
                print(f"Found ADB at: {path}")
                return str(path)
                
        raise FileNotFoundError("Could not find ADB executable. Please ensure Android SDK platform-tools is installed.")

    def check_adb_connection(self):
        """Check if ADB is connected and working"""
        try:
            subprocess.run([self.adb_path, 'devices'], check=True)
        except subprocess.CalledProcessError:
            raise Exception("ADB is not properly connected. Please check your device connection.")
            
    def swipe_left(self):
        """Swipe left on the screen"""
        subprocess.run([self.adb_path, 'shell', 'input', 'swipe', '500', '1000', '100', '1000', '100'])
        
    def swipe_right(self):
        """Swipe right on the screen"""
        subprocess.run([self.adb_path, 'shell', 'input', 'swipe', '100', '1000', '500', '1000', '100'])
        
    def swipe_up(self):
        """Swipe up (jump) on the screen"""
        subprocess.run([self.adb_path, 'shell', 'input', 'swipe', '300', '1000', '300', '500', '100'])
        
    def swipe_down(self):
        """Swipe down (slide) on the screen"""
        subprocess.run([self.adb_path, 'shell', 'input', 'swipe', '300', '500', '300', '1000', '100'])
        
    def take_screenshot(self, output_path):
        """Take a screenshot of the device screen"""
        # Take screenshot
        subprocess.run([self.adb_path, 'shell', 'screencap', '-p', '/sdcard/screenshot.png'])
        
        # Pull the screenshot to computer
        subprocess.run([self.adb_path, 'pull', '/sdcard/screenshot.png', str(output_path)])
        
        # Delete screenshot from device
        subprocess.run([self.adb_path, 'shell', 'rm', '/sdcard/screenshot.png'])
        
    def perform_action(self, action):
        """Perform the specified action"""
        if action == 'left':
            self.swipe_left()
        elif action == 'right':
            self.swipe_right()
        elif action == 'jump':
            self.swipe_up()
        elif action == 'down':
            self.swipe_down()
        elif action == 'running':
            # Do nothing for running state
            pass
        else:
            raise ValueError(f"Unknown action: {action}")
            
    def start_game(self):
        """Start the Subway Surfers game"""
        subprocess.run([self.adb_path, 'shell', 'am', 'start', '-n', 'com.kiloo.subwaysurf/.SubwaySurf'])
        time.sleep(5)  # Wait for game to load
        
    def stop_game(self):
        """Stop the Subway Surfers game"""
        subprocess.run([self.adb_path, 'shell', 'am', 'force-stop', 'com.kiloo.subwaysurf']) 