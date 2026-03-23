"""
LSTM Model Architecture
Deep learning model for student performance prediction
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
import numpy as np
import os


class StudentPerformanceLSTM:
    """
    LSTM model for predicting student engagement and performance
    """
    
    def __init__(self, sequence_length=3, n_features=8):
        """
        Initialize LSTM model
        
        Args:
            sequence_length (int): Length of input sequences
            n_features (int): Number of features per timestep
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None
        self.history = None
        
    def build_model(self, lstm_units=[128, 64], dropout_rate=0.3, learning_rate=0.001):
        """
        Build multi-layer LSTM architecture
        
        Args:
            lstm_units (list): Number of units in each LSTM layer
            dropout_rate (float): Dropout rate for regularization
            learning_rate (float): Learning rate for optimizer
            
        Returns:
            keras.Model: Compiled model
        """
        self.model = Sequential([
            # First LSTM layer (Bidirectional for better context)
            Bidirectional(
                LSTM(lstm_units[0], return_sequences=True, 
                     input_shape=(self.sequence_length, self.n_features)),
                name='bidirectional_lstm_1'
            ),
            Dropout(dropout_rate, name='dropout_1'),
            
            # Second LSTM layer
            LSTM(lstm_units[1], return_sequences=False, name='lstm_2'),
            Dropout(dropout_rate, name='dropout_2'),
            
            # Dense layers
            Dense(32, activation='relu', name='dense_1'),
            Dropout(dropout_rate / 2, name='dropout_3'),
            
            Dense(16, activation='relu', name='dense_2'),
            
            # Output layer (predicting engagement score 0-1)
            Dense(1, activation='sigmoid', name='output')
        ])
        
        # Compile model
        optimizer = Adam(learning_rate=learning_rate)
        self.model.compile(
            optimizer=optimizer,
            loss='mse',
            metrics=['mae', 'mse']
        )
        
        print("\n=== LSTM Model Architecture ===")
        self.model.summary()
        
        return self.model
    
    def get_callbacks(self, model_path=None, patience=15):
        """
        Create training callbacks
        
        Args:
            model_path (str): Path to save best model
            patience (int): Early stopping patience
            
        Returns:
            list: List of callbacks
        """
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'models', 'lstm_model.h5')
        
        callbacks = [
            # Early stopping to prevent overfitting
            EarlyStopping(
                monitor='val_loss',
                patience=patience,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Reduce learning rate when validation loss plateaus
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            
            # Save best model
            ModelCheckpoint(
                model_path,
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            )
        ]
        
        return callbacks
    
    def train(self, X_train, y_train, X_val, y_val, 
              epochs=100, batch_size=32, verbose=1):
        """
        Train the LSTM model
        
        Args:
            X_train (np.array): Training sequences
            y_train (np.array): Training targets
            X_val (np.array): Validation sequences
            y_val (np.array): Validation targets
            epochs (int): Maximum number of epochs
            batch_size (int): Batch size
            verbose (int): Verbosity level
            
        Returns:
            keras.History: Training history
        """
        if self.model is None:
            self.build_model()
        
        print("\n=== Training LSTM Model ===")
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Batch size: {batch_size}")
        print(f"Max epochs: {epochs}\n")
        
        callbacks = self.get_callbacks()
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        print("\n=== Training Complete ===")
        return self.history
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        
        Args:
            X_test (np.array): Test sequences
            y_test (np.array): Test targets
            
        Returns:
            dict: Evaluation metrics
        """
        print("\n=== Evaluating Model ===")
        results = self.model.evaluate(X_test, y_test, verbose=0)
        
        metrics = {
            'loss': results[0],
            'mae': results[1],
            'mse': results[2],
            'rmse': np.sqrt(results[2])
        }
        
        print(f"Test Loss: {metrics['loss']:.4f}")
        print(f"Test MAE: {metrics['mae']:.4f}")
        print(f"Test RMSE: {metrics['rmse']:.4f}")
        
        return metrics
    
    def predict(self, X):
        """
        Make predictions
        
        Args:
            X (np.array): Input sequences
            
        Returns:
            np.array: Predictions
        """
        predictions = self.model.predict(X, verbose=0)
        return predictions
    
    def save_model(self, model_path=None):
        """
        Save trained model
        
        Args:
            model_path (str): Path to save model
        """
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'models', 'lstm_model.h5')
        
        self.model.save(model_path)
        print(f"\nModel saved to {model_path}")
    
    def load_model(self, model_path=None):
        """
        Load a trained model
        
        Args:
            model_path (str): Path to model file
        """
        if model_path is None:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'models', 'lstm_model.h5')
        
        # Disable compilation to avoid legacy HDF5 deserialization issues in Keras 3
        self.model = keras.models.load_model(model_path, compile=False)
        print(f"Model loaded from {model_path}")
    
    def get_training_history(self):
        """
        Get training history metrics
        
        Returns:
            dict: Training history
        """
        if self.history is None:
            return None
        
        return {
            'loss': self.history.history['loss'],
            'val_loss': self.history.history['val_loss'],
            'mae': self.history.history['mae'],
            'val_mae': self.history.history['val_mae']
        }


def create_lstm_model(sequence_length=3, n_features=8):
    """
    Factory function to create LSTM model
    
    Args:
        sequence_length (int): Sequence length
        n_features (int): Number of features
        
    Returns:
        StudentPerformanceLSTM: Initialized model
    """
    model = StudentPerformanceLSTM(sequence_length, n_features)
    model.build_model()
    return model


if __name__ == "__main__":
    # Test model creation
    print("Creating LSTM model...")
    model = create_lstm_model()
    print("\nModel created successfully!")
