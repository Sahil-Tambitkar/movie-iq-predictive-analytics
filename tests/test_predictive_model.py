import pytest
import pandas as pd
import numpy as np
import os
from unittest.mock import patch, MagicMock

from src.models.predictive_model import train_and_save_model

@patch('src.models.predictive_model.joblib.dump')
@patch('src.models.predictive_model.plt.savefig')
def test_train_and_save_model(mock_savefig, mock_joblib_dump, tmp_path):
    # Create dummy data for training
    # Needs enough rows to satisfy GridSearchCV with cv=3
    n_samples = 30
    
    np.random.seed(42)
    X_train = pd.DataFrame({
        'budget': np.random.rand(n_samples) * 1000000,
        'popularity': np.random.rand(n_samples) * 100,
        'runtime': np.random.rand(n_samples) * 120,
        'vote_average': np.random.rand(n_samples) * 10
    })
    y_train = pd.Series(np.random.randint(0, 2, size=n_samples))
    
    X_test = pd.DataFrame({
        'budget': np.random.rand(10) * 1000000,
        'popularity': np.random.rand(10) * 100,
        'runtime': np.random.rand(10) * 120,
        'vote_average': np.random.rand(10) * 10
    })
    y_test = pd.Series(np.random.randint(0, 2, size=10))
    
    features = list(X_train.columns)
    
    # Use temporary paths to avoid writing to real directories
    model_path = str(tmp_path / "model.pkl")
    features_path = str(tmp_path / "model_features.pkl")
    
    # Run the function
    train_and_save_model(
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        features=features,
        model_path=model_path,
        features_path=features_path
    )
    
    # Assertions
    # Joblib dump should be called twice (for model and features)
    assert mock_joblib_dump.call_count == 2
    
    # Assert plot saves were called
    assert mock_savefig.call_count >= 2
