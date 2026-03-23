"""
Training Pipeline
Trains LSTM model and generates visualizations
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from data_preprocessing import preprocess_pipeline
from lstm_model import StudentPerformanceLSTM
import os
import json
from datetime import datetime


def plot_training_history(history, output_path=None):
    """
    Plot training and validation metrics
    
    Args:
        history (dict): Training history
        output_path (str): Path to save plot
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'outputs', 'graphs', 'training_metrics.png')
    
    # Set style
    sns.set_style("whitegrid")
    plt.figure(figsize=(15, 5))
    
    # Plot loss
    plt.subplot(1, 3, 1)
    plt.plot(history['loss'], label='Training Loss', linewidth=2, color='#3498db')
    plt.plot(history['val_loss'], label='Validation Loss', linewidth=2, color='#e74c3c')
    plt.title('Model Loss Over Epochs', fontsize=14, fontweight='bold')
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss (MSE)', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Plot MAE
    plt.subplot(1, 3, 2)
    plt.plot(history['mae'], label='Training MAE', linewidth=2, color='#2ecc71')
    plt.plot(history['val_mae'], label='Validation MAE', linewidth=2, color='#f39c12')
    plt.title('Mean Absolute Error', fontsize=14, fontweight='bold')
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('MAE', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Plot comparison
    plt.subplot(1, 3, 3)
    epochs = range(1, len(history['loss']) + 1)
    plt.plot(epochs, history['loss'], label='Train Loss', linewidth=2, color='#3498db', alpha=0.7)
    plt.plot(epochs, history['val_loss'], label='Val Loss', linewidth=2, color='#e74c3c', alpha=0.7)
    plt.fill_between(epochs, history['loss'], alpha=0.2, color='#3498db')
    plt.fill_between(epochs, history['val_loss'], alpha=0.2, color='#e74c3c')
    plt.title('Training vs Validation Loss', fontsize=14, fontweight='bold')
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nTraining metrics plot saved to {output_path}")
    plt.close()


def plot_predictions_vs_actual(y_true, y_pred, output_path=None):
    """
    Plot predicted vs actual values
    
    Args:
        y_true (np.array): True values
        y_pred (np.array): Predicted values
        output_path (str): Path to save plot
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'outputs', 'graphs', 'predictions.png')
    
    plt.figure(figsize=(12, 5))
    
    # Scatter plot
    plt.subplot(1, 2, 1)
    plt.scatter(y_true, y_pred, alpha=0.5, color='#3498db', edgecolors='black', linewidth=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 
             'r--', linewidth=2, label='Perfect Prediction')
    plt.xlabel('Actual Engagement Score', fontsize=12)
    plt.ylabel('Predicted Engagement Score', fontsize=12)
    plt.title('Predicted vs Actual Values', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Residual plot
    plt.subplot(1, 2, 2)
    residuals = y_true - y_pred.flatten()
    plt.scatter(y_pred, residuals, alpha=0.5, color='#e74c3c', edgecolors='black', linewidth=0.5)
    plt.axhline(y=0, color='black', linestyle='--', linewidth=2)
    plt.xlabel('Predicted Values', fontsize=12)
    plt.ylabel('Residuals', fontsize=12)
    plt.title('Residual Plot', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Predictions plot saved to {output_path}")
    plt.close()


def save_training_summary(metrics, stats, history, output_path=None):
    """
    Save training summary to JSON
    
    Args:
        metrics (dict): Evaluation metrics
        stats (dict): Data statistics
        history (dict): Training history
        output_path (str): Path to save summary
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'outputs', 'training_summary.json')
    
    summary = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'model_metrics': metrics,
        'data_statistics': stats,
        'training_history': history
    }
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=4)
    
    print(f"Training summary saved to {output_path}")


def train_model(epochs=100, batch_size=32, sequence_length=3):
    """
    Complete training pipeline
    
    Args:
        epochs (int): Number of training epochs
        batch_size (int): Batch size
        sequence_length (int): Sequence length
        
    Returns:
        tuple: model, metrics, history
    """
    print("=" * 60)
    print("AI E-LEARNING ANALYTICS - LSTM MODEL TRAINING")
    print("=" * 60)
    
    # Step 1: Preprocess data
    print("\n[1/5] Preprocessing data...")
    X_train, X_test, y_train, y_test, preprocessor, stats = preprocess_pipeline(
        sequence_length=sequence_length
    )
    
    # Step 2: Create model
    print("\n[2/5] Building LSTM model...")
    model = StudentPerformanceLSTM(
        sequence_length=sequence_length, 
        n_features=X_train.shape[2]
    )
    model.build_model(lstm_units=[128, 64], dropout_rate=0.3)
    
    # Step 3: Train model
    print("\n[3/5] Training model...")
    history = model.train(
        X_train, y_train,
        X_test, y_test,
        epochs=epochs,
        batch_size=batch_size,
        verbose=1
    )
    
    # Step 4: Evaluate model
    print("\n[4/5] Evaluating model...")
    metrics = model.evaluate(X_test, y_test)
    
    # Step 5: Generate visualizations
    print("\n[5/5] Generating visualizations...")
    training_history = model.get_training_history()
    plot_training_history(training_history)
    
    # Make predictions and plot
    y_pred = model.predict(X_test)
    plot_predictions_vs_actual(y_test, y_pred)
    
    # Save summary
    save_training_summary(metrics, stats, training_history)
    
    # Save model
    model.save_model()
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"\nFinal Metrics:")
    print(f"  Test Loss (MSE): {metrics['loss']:.4f}")
    print(f"  Test MAE: {metrics['mae']:.4f}")
    print(f"  Test RMSE: {metrics['rmse']:.4f}")
    print(f"\nModel saved: models/lstm_model.h5")
    print(f"Graphs saved: outputs/graphs/")
    print(f"Summary saved: outputs/training_summary.json")
    
    return model, metrics, training_history


if __name__ == "__main__":
    # Train the model
    model, metrics, history = train_model(epochs=100, batch_size=32, sequence_length=3)
