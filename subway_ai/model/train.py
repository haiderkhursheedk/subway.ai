import tensorflow as tf
import numpy as np
from pathlib import Path
import json
import sys

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))
from utils.preprocess import load_and_preprocess_data

def build_model():
    """
    Build and return the CNN model for action prediction
    """
    model = tf.keras.Sequential([
        # Input layer
        tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(84, 84, 3)),
        tf.keras.layers.MaxPooling2D((2, 2)),
        
        # First convolutional block
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        
        # Second convolutional block
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        
        # Third convolutional block
        tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2, 2)),
        
        # Flatten and dense layers
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(5, activation='softmax')  # 5 actions: left, right, jump, down, running
    ])
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model():
    """
    Train the model on the labeled frames
    """
    # Load and preprocess data
    frames_dir = Path("data/frames")
    labels_file = Path("data/labeled_frames/labels.json")
    
    # Check if labels exist
    if not labels_file.exists():
        raise FileNotFoundError(f"Labels file not found at {labels_file}. Please run label_frames.py first.")
    
    dataset = load_and_preprocess_data(frames_dir, labels_file)
    
    # Split dataset into train and validation
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset = dataset.take(train_size)
    val_dataset = dataset.skip(train_size).take(val_size)
    
    # Add .repeat() to prevent dataset exhaustion
    train_dataset = train_dataset.repeat()
    val_dataset = val_dataset.repeat()
    
    # Build model
    model = build_model()
    
    # Create checkpoint callback with simpler naming
    checkpoint_dir = Path("model/checkpoint")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_dir / "model_{epoch:02d}.h5"
    
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        str(checkpoint_path),
        save_best_only=True,
        monitor='loss'  # Changed from val_accuracy to loss
    )
    
    # Calculate steps per epoch
    steps_per_epoch = max(train_size // 32, 1)  # Using batch_size=32
    validation_steps = max(val_size // 32, 1)
    
    # Train model
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=50,
        steps_per_epoch=steps_per_epoch,
        validation_steps=validation_steps,
        callbacks=[
            checkpoint_callback,
            tf.keras.callbacks.EarlyStopping(
                monitor='loss',  # Changed from val_accuracy to loss
                patience=5,
                restore_best_weights=True
            )
        ]
    )
    
    # Save final model
    model.save("model/model.h5")
    
    # Save training history
    with open("model/training_history.json", 'w') as f:
        json.dump(history.history, f)

if __name__ == "__main__":
    train_model() 