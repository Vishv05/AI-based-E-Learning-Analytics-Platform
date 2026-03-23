"""
AI E-Learning Analytics Platform
Main Entry Point for Model Pipeline
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.train import train_model
from src.predict import predict_pipeline


def main():
    """
    Main execution pipeline
    """
    print("\n" + "=" * 70)
    print("AI E-LEARNING ANALYTICS PLATFORM - COMPLETE PIPELINE")
    print("=" * 70)
    print("\nThis will execute the complete AI pipeline:")
    print("1. Data preprocessing")
    print("2. LSTM model training")
    print("3. Model evaluation")
    print("4. Student predictions")
    print("\nThis may take several minutes...")
    print("=" * 70 + "\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Execution cancelled.")
        return
    
    try:
        # Step 1: Train model
        print("\n" + "=" * 70)
        print("STEP 1: TRAINING LSTM MODEL")
        print("=" * 70 + "\n")
        
        model, metrics, history = train_model(epochs=100, batch_size=32, sequence_length=3)
        
        # Step 2: Generate predictions
        print("\n" + "=" * 70)
        print("STEP 2: GENERATING PREDICTIONS")
        print("=" * 70 + "\n")
        
        predictions = predict_pipeline()
        
        # Summary
        print("\n" + "=" * 70)
        print("PIPELINE COMPLETE!")
        print("=" * 70)
        print("\nModel Performance:")
        print(f"  Test Loss (MSE): {metrics['loss']:.4f}")
        print(f"  Test MAE: {metrics['mae']:.4f}")
        print(f"  Test RMSE: {metrics['rmse']:.4f}")
        
        print("\nPredictions:")
        print(f"  Total students analyzed: {len(predictions)}")
        print(f"  Average engagement score: {predictions['engagement_score'].mean():.2f}/10")
        
        print("\nGenerated Files:")
        print("  ✓ models/lstm_model.h5 - Trained LSTM model")
        print("  ✓ models/scaler.pkl - Data scaler")
        print("  ✓ data/processed/cleaned_data.csv - Processed data")
        print("  ✓ outputs/graphs/training_metrics.png - Training visualizations")
        print("  ✓ outputs/graphs/predictions.png - Prediction plots")
        print("  ✓ outputs/predictions/results.csv - Student predictions")
        print("  ✓ outputs/training_summary.json - Training summary")
        
        print("\nNext Steps:")
        print("  Run the web application: python app.py")
        print("  Then open: http://127.0.0.1:5000")
        
        print("\n" + "=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
