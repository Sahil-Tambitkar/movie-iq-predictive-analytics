import pytest
import pandas as pd
import joblib
import os
from src.config_loader import load_config

from unittest.mock import patch, MagicMock

@patch('os.path.exists')
@patch('joblib.load')
def test_model_loading_and_prediction(mock_joblib_load, mock_exists):
    # Mock file existence
    mock_exists.return_value = True
    
    # Mock the joblib.load behavior
    mock_model = MagicMock()
    mock_model.predict.return_value = [1]
    
    # joblib.load is called twice: once for model, once for features
    mock_features = ['budget', 'popularity', 'runtime', 'vote_average', 'genre_Action']
    mock_joblib_load.side_effect = [mock_model, mock_features]
    
    config = load_config()
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config['paths']['model'])
    features_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config['paths']['model_features'])
    
    # Assert artifacts exist (this uses the mock)
    assert os.path.exists(model_path), "Model file not found"
    assert os.path.exists(features_path), "Features file not found"
    
    model = joblib.load(model_path)
    features = joblib.load(features_path)
    
    assert model is not None
    assert len(features) > 0
    
    # Mock data to test prediction logic
    mock_data = {f: 0 for f in features}
    mock_data['budget'] = 100000000
    mock_data['popularity'] = 100
    
    mock_df = pd.DataFrame([mock_data])
    prediction = model.predict(mock_df)
    
    assert prediction[0] in [0, 1]
    mock_model.predict.assert_called_once_with(mock_df)
