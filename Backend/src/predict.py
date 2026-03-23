"""
Prediction Module
Loads trained model and makes predictions on new data
"""

import numpy as np
import pandas as pd
import pickle
import os


class StudentPredictor:
    """
    Prediction service for student performance
    """
    
    def __init__(self, model_path=None, scaler_path=None):
        """
        Initialize predictor
        
        Args:
            model_path (str): Path to trained model
            scaler_path (str): Path to fitted scaler
        """
        base_dir = os.path.dirname(os.path.dirname(__file__))
        
        if model_path is None:
            model_path = os.path.join(base_dir, 'models', 'lstm_model.h5')
        if scaler_path is None:
            scaler_path = os.path.join(base_dir, 'models', 'scaler.pkl')
        
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self.feature_columns = [
            'login_count', 'time_spent_hours', 'quiz_score', 
            'assignment_score', 'forum_posts', 'video_completion_rate',
            'course_progress', 'engagement_score'
        ]
        
    def load_model(self):
        """Load trained LSTM model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}. Please train the model first.")

        # Import here to avoid TensorFlow import on module load.
        from lstm_model import StudentPerformanceLSTM

        lstm = StudentPerformanceLSTM()
        lstm.load_model(self.model_path)
        self.model = lstm.model
        print("Model loaded successfully")
    
    def load_scaler(self):
        """Load fitted scaler"""
        if not os.path.exists(self.scaler_path):
            raise FileNotFoundError(f"Scaler not found at {self.scaler_path}. Please train the model first.")
        
        with open(self.scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        print("Scaler loaded successfully")
    
    def prepare_sequence(self, data):
        """
        Prepare data sequence for prediction
        
        Args:
            data (np.array or pd.DataFrame): Student activity data
            
        Returns:
            np.array: Normalized sequence
        """
        if isinstance(data, pd.DataFrame):
            data = data[self.feature_columns].values
        
        # Normalize
        normalized = self.scaler.transform(data)
        
        return normalized
    
    def predict_engagement(self, sequence_data):
        """
        Predict future engagement score
        
        Args:
            sequence_data (np.array): Sequence of student activities (time_steps, features)
            
        Returns:
            float: Predicted engagement score
        """
        if self.model is None:
            self.load_model()
        if self.scaler is None:
            self.load_scaler()
        
        # Prepare sequence
        if len(sequence_data.shape) == 2:
            # Single sequence
            sequence = self.prepare_sequence(sequence_data)
            sequence = np.expand_dims(sequence, axis=0)
        else:
            # Multiple sequences
            sequence = sequence_data
        
        # Predict
        prediction = self.model.predict(sequence, verbose=0)
        
        return prediction[0][0] if len(prediction) == 1 else prediction.flatten()
    
    def predict_student_risk(self, engagement_score):
        """
        Classify student risk level based on engagement
        
        Args:
            engagement_score (float): Predicted engagement score (0-1)
            
        Returns:
            dict: Risk assessment
        """
        # Convert to 0-10 scale
        score = engagement_score * 10
        
        if score >= 8.0:
            risk_level = "Low Risk"
            status = "Excellent"
            color = "#2ecc71"
            recommendation = "Student is performing exceptionally well. Continue current support."
        elif score >= 6.5:
            risk_level = "Medium-Low Risk"
            status = "Good"
            color = "#3498db"
            recommendation = "Student is on track. Monitor progress and provide encouragement."
        elif score >= 5.0:
            risk_level = "Medium Risk"
            status = "Needs Attention"
            color = "#f39c12"
            recommendation = "Student needs additional support. Consider tutoring or extra resources."
        else:
            risk_level = "High Risk"
            status = "At Risk"
            color = "#e74c3c"
            recommendation = "URGENT: Student is at risk of dropout. Immediate intervention required."
        
        return {
            'engagement_score': round(score, 2),
            'risk_level': risk_level,
            'status': status,
            'color': color,
            'recommendation': recommendation
        }
    
    def predict_for_student(self, student_data):
        """
        Make complete prediction for a student
        
        Args:
            student_data (pd.DataFrame or np.array): Recent student activity (last 3 weeks)
            
        Returns:
            dict: Complete prediction results
        """
        # Predict engagement
        engagement = self.predict_engagement(student_data)
        
        # Get risk assessment
        risk = self.predict_student_risk(engagement)
        
        return risk
    
    def batch_predict(self, data_path):
        """
        Make predictions for all students in dataset
        
        Args:
            data_path (str): Path to student data CSV
            
        Returns:
            pd.DataFrame: Predictions for all students
        """
        df = pd.read_csv(data_path)
        results = []
        
        for student_id in df['student_id'].unique():
            student_data = df[df['student_id'] == student_id].tail(3)
            
            if len(student_data) >= 3:
                try:
                    prediction = self.predict_for_student(student_data)
                    prediction['student_id'] = student_id
                    results.append(prediction)
                except Exception as e:
                    print(f"Error predicting for student {student_id}: {e}")
        
        return pd.DataFrame(results)
    
    def save_predictions(self, predictions_df, output_path=None):
        """
        Save predictions to CSV
        
        Args:
            predictions_df (pd.DataFrame): Predictions dataframe
            output_path (str): Output path
        """
        if output_path is None:
            output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       'outputs', 'predictions', 'results.csv')
        
        predictions_df.to_csv(output_path, index=False)
        print(f"Predictions saved to {output_path}")


def predict_pipeline(data_path=None):
    """
    Complete prediction pipeline
    
    Args:
        data_path (str): Path to data file
        
    Returns:
        pd.DataFrame: Predictions
    """
    if data_path is None:
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'data', 'processed', 'cleaned_data.csv')
    
    print("=" * 60)
    print("AI E-LEARNING ANALYTICS - STUDENT PREDICTIONS")
    print("=" * 60)
    
    # Initialize predictor
    predictor = StudentPredictor()
    
    # Make predictions
    print("\nGenerating predictions for all students...")
    predictions = predictor.batch_predict(data_path)
    
    # Save predictions
    predictor.save_predictions(predictions)
    
    # Display summary
    print("\n=== Prediction Summary ===")
    print(f"Total students analyzed: {len(predictions)}")
    print(f"\nRisk Distribution:")
    for risk_level in predictions['risk_level'].unique():
        count = len(predictions[predictions['risk_level'] == risk_level])
        print(f"  {risk_level}: {count} students")
    
    print(f"\nAverage Engagement Score: {predictions['engagement_score'].mean():.2f}/10")
    
    return predictions


if __name__ == "__main__":
    # Run prediction pipeline
    predictions = predict_pipeline()
    print("\n" + "=" * 60)
    print("PREDICTIONS COMPLETE!")
    print("=" * 60)
