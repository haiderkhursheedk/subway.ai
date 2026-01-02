import cv2
import numpy as np
from pathlib import Path
import tensorflow as tf
import json

def preprocess_frame(frame, target_size=(84, 84)):
    """
    Preprocess a single frame for model input
    
    Args:
        frame: Input frame (numpy array)
        target_size: Target size for the frame (height, width)
    
    Returns:
        Preprocessed frame
    """
    # Resize frame
    frame = tf.image.resize(frame, target_size)
    # Normalize pixel values
    frame = frame / 255.0
    return frame

def load_and_preprocess_data(frames_dir, labels_file, batch_size=32):
    """
    Create a TensorFlow dataset from frames and labels
    
    Args:
        frames_dir: Directory containing frames
        labels_file: JSON file containing frame labels
        batch_size: Batch size for training
    
    Returns:
        TensorFlow dataset
    """
    # Load labels
    with open(labels_file, 'r') as f:
        labels = json.load(f)
    
    # Create lists for frames and labels
    frame_paths = []
    label_values = []
    
    # Convert labels to numerical values
    label_map = {'left': 0, 'right': 1, 'jump': 2, 'down': 3, 'running': 4}
    
    for frame_name, label in labels.items():
        frame_path = str(Path(frames_dir) / frame_name)
        frame_paths.append(frame_path)
        label_values.append(label_map[label])
    
    # Convert to tensors
    frame_paths = tf.constant(frame_paths)
    label_values = tf.constant(label_values, dtype=tf.int32)
    
    # Create dataset
    dataset = tf.data.Dataset.from_tensor_slices((frame_paths, label_values))
    
    def load_and_preprocess_frame(path, label):
        # Convert path tensor to string
        path = tf.cast(path, tf.string)
        # Read image file
        image = tf.io.read_file(path)
        # Decode JPEG
        image = tf.image.decode_jpeg(image, channels=3)
        # Convert to float32
        image = tf.cast(image, tf.float32)
        # Preprocess
        image = preprocess_frame(image)
        return image, label
    
    # Map preprocessing function
    dataset = dataset.map(load_and_preprocess_frame, 
                         num_parallel_calls=tf.data.AUTOTUNE)
    
    # Shuffle and batch
    dataset = dataset.shuffle(1000)
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    
    return dataset

def main():
    # Example usage
    frames_dir = "data/labeled_frames"
    labels_file = "data/labeled_frames/labels.json"
    dataset = load_and_preprocess_data(frames_dir, labels_file)
    
    # Print dataset info
    for frames, labels in dataset.take(1):
        print(f"Batch shape: {frames.shape}")
        print(f"Labels shape: {labels.shape}")

if __name__ == "__main__":
    main() 