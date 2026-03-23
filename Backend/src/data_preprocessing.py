"""
Data Preprocessing Module
Handles data loading, cleaning, normalization, and sequence generation for LSTM
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import os
import pickle


class DataPreprocessor:
    """
    Preprocesses student learning data for LSTM model training
    """
    
    def __init__(self, data_path=None):
        """
        Initialize preprocessor
        
        Args:
            data_path (str): Path to raw data CSV file
        """
        if data_path is None:
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'data', 'raw', 'student_activity.csv')
        self.data_path = data_path
        self.scaler = MinMaxScaler()
        self.feature_columns = [
            'login_count', 'time_spent_hours', 'quiz_score', 
            'assignment_score', 'forum_posts', 'video_completion_rate',
            'course_progress', 'engagement_score'
        ]
        
    def load_data(self):
        """
        Load raw student activity data
        
        Returns:
            pd.DataFrame: Loaded data
        """
        print(f"Loading data from {self.data_path}")
        df = pd.read_csv(self.data_path)
        print(f"Loaded {len(df)} records for {df['student_id'].nunique()} students")
        return df
    
    def clean_data(self, df):
        """
        Clean and validate data
        
        Args:
            df (pd.DataFrame): Raw dataframe
            
        Returns:
            pd.DataFrame: Cleaned dataframe
        """
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.fillna(method='ffill').fillna(0)
        
        # Sort by student and week
        df = df.sort_values(['student_id', 'week'])
        
        # Validate ranges
        df['quiz_score'] = df['quiz_score'].clip(0, 100)
        df['assignment_score'] = df['assignment_score'].clip(0, 100)
        df['video_completion_rate'] = df['video_completion_rate'].clip(0, 1)
        df['course_progress'] = df['course_progress'].clip(0, 100)
        
        print(f"Data cleaned: {len(df)} records retained")
        return df
    
    def create_sequences(self, data, sequence_length=3, target_column='engagement_score'):
        """
        Create sequences for LSTM training
        
        Args:
            data (np.array): Normalized feature data
            sequence_length (int): Length of input sequences
            target_column (str): Column to predict
            
        Returns:
            tuple: X (sequences), y (targets)
        """
        X, y = [], []
        
        for i in range(len(data) - sequence_length):
            X.append(data[i:i+sequence_length])
            y.append(data[i+sequence_length, -1])  # Predict engagement_score
        
        return np.array(X), np.array(y)
    
    def prepare_student_sequences(self, df, sequence_length=3):
        """
        Prepare sequences grouped by student
        
        Args:
            df (pd.DataFrame): Cleaned dataframe
            sequence_length (int): Length of sequences
            
        Returns:
            tuple: X_train, X_test, y_train, y_test
        """
        all_X = []
        all_y = []

        # Fit scaler on full dataset for consistent normalization
        full_feature_data = df[self.feature_columns].values
        self.scaler.fit(full_feature_data)
        
        # Process each student separately
        for student_id in df['student_id'].unique():
            student_data = df[df['student_id'] == student_id][self.feature_columns].values
            
            # Only create sequences if student has enough data
            if len(student_data) > sequence_length:
                # Normalize
                normalized_data = self.scaler.transform(student_data)
                
                # Create sequences
                X_seq, y_seq = self.create_sequences(normalized_data, sequence_length)
                
                if len(X_seq) > 0:
                    all_X.append(X_seq)
                    all_y.append(y_seq)
        
        # Combine all sequences
        X = np.vstack(all_X)
        y = np.concatenate(all_y)
        
        print(f"Created {len(X)} sequences with shape {X.shape}")
        
        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        return X_train, X_test, y_train, y_test
    
    def save_processed_data(self, df, output_path=None):
        """
        Save cleaned data
        
        Args:
            df (pd.DataFrame): Cleaned dataframe
            output_path (str): Path to save processed data
        """
        if output_path is None:
            output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       'data', 'processed', 'cleaned_data.csv')
        
        df.to_csv(output_path, index=False)
        print(f"Processed data saved to {output_path}")
    
    def save_scaler(self, scaler_path=None):
        """
        Save the fitted scaler for later use
        
        Args:
            scaler_path (str): Path to save scaler
        """
        if scaler_path is None:
            scaler_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       'models', 'scaler.pkl')
        
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"Scaler saved to {scaler_path}")
    
    def load_scaler(self, scaler_path=None):
        """
        Load a saved scaler
        
        Args:
            scaler_path (str): Path to scaler file
        """
        if scaler_path is None:
            scaler_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       'models', 'scaler.pkl')
        
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        print(f"Scaler loaded from {scaler_path}")
    
    def get_statistics(self, df):
        """
        Calculate summary statistics
        
        Args:
            df (pd.DataFrame): Dataframe to analyze
            
        Returns:
            dict: Summary statistics
        """
        stats = {
            'total_students': df['student_id'].nunique(),
            'total_records': len(df),
            'avg_engagement': df['engagement_score'].mean(),
            'avg_quiz_score': df['quiz_score'].mean(),
            'avg_time_spent': df['time_spent_hours'].mean(),
            'completion_rate': (df.groupby('student_id')['course_progress'].max() == 100).mean() * 100
        }
        return stats


def preprocess_pipeline(data_path=None, sequence_length=3):
    """
    Complete preprocessing pipeline
    
    Args:
        data_path (str): Path to raw data
        sequence_length (int): Sequence length for LSTM
        
    Returns:
        tuple: X_train, X_test, y_train, y_test, preprocessor, stats
    """
    # Initialize preprocessor
    preprocessor = DataPreprocessor(data_path)
    
    # Load and clean data
    df = preprocessor.load_data()
    df = preprocessor.clean_data(df)
    
    # Save processed data
    preprocessor.save_processed_data(df)
    
    # Get statistics
    stats = preprocessor.get_statistics(df)
    
    # Prepare sequences
    X_train, X_test, y_train, y_test = preprocessor.prepare_student_sequences(
        df, sequence_length
    )
    
    # Save scaler
    preprocessor.save_scaler()
    
    print("\n=== Preprocessing Complete ===")
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    print(f"Sequence shape: {X_train.shape}")
    print(f"Average engagement: {stats['avg_engagement']:.2f}")
    
    return X_train, X_test, y_train, y_test, preprocessor, stats


if __name__ == "__main__":
    # Run preprocessing pipeline
    X_train, X_test, y_train, y_test, preprocessor, stats = preprocess_pipeline()
    print("\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value:.2f}")
