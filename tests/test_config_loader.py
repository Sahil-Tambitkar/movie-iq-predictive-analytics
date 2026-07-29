import pytest
import os
import json
from unittest.mock import patch, mock_open
from src.config_loader import load_config

def test_load_config_no_metadata():
    yaml_content = "paths:\n  model: 'dummy_model.pkl'\n  model_features: 'dummy_features.pkl'\n"
    
    with patch('os.path.exists', return_value=False), \
         patch('builtins.open', mock_open(read_data=yaml_content)):
        config = load_config()
        assert config['paths']['model'] == 'dummy_model.pkl'

def test_load_config_with_metadata():
    yaml_content = "paths:\n  model: 'dummy_model.pkl'\n  model_features: 'dummy_features.pkl'\n"
    metadata_content = '{"model_path": "new_model.pkl", "model_features_path": "new_features.pkl", "model_hmac": "hmac1", "model_features_hmac": "hmac2"}'
    
    def side_effect(filename, *args, **kwargs):
        if filename.endswith('config.yaml'):
            return mock_open(read_data=yaml_content).return_value
        elif filename.endswith('metadata.json'):
            return mock_open(read_data=metadata_content).return_value
        return mock_open(read_data="").return_value

    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', side_effect=side_effect):
        config = load_config()
        assert config['paths']['model'] == 'new_model.pkl'
        assert config['model_hmac'] == 'hmac1'

def test_load_config_metadata_invalid_json():
    yaml_content = "paths:\n  model: 'dummy_model.pkl'\n  model_features: 'dummy_features.pkl'\n"
    metadata_content = 'invalid json'
    
    def side_effect(filename, *args, **kwargs):
        if filename.endswith('config.yaml'):
            return mock_open(read_data=yaml_content).return_value
        elif filename.endswith('metadata.json'):
            return mock_open(read_data=metadata_content).return_value
        return mock_open(read_data="").return_value

    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', side_effect=side_effect):
        config = load_config()
        assert config['paths']['model'] == 'dummy_model.pkl'  # Fallback to yaml
