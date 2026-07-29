import pytest
import pandas as pd
import json
import os
from unittest.mock import patch, MagicMock, mock_open

from src.pipeline import run_pipeline, generate_eda_artifacts

@patch('src.pipeline.plt.savefig')
def test_generate_eda_artifacts(mock_savefig):
    df = pd.DataFrame({
        'budget': [1000, 2000],
        'revenue': [2000, 4000],
        'popularity': [10.5, 20.1],
        'runtime': [90, 120],
        'vote_average': [6.5, 8.0],
        'success': [0, 1],
        'genre_list': [['Action'], ['Comedy', 'Drama']]
    })
    
    generate_eda_artifacts(df)
    
    # Assert plots are saved
    assert mock_savefig.call_count >= 4

@patch('src.pipeline.load_and_clean_data')
@patch('src.pipeline.generate_eda_artifacts')
@patch('src.pipeline.get_top_genres')
@patch('src.pipeline.train_and_save_model')
@patch('json.dump')
@patch('src.utils.generate_file_hmac')
@patch('src.config_loader.load_config')
def test_run_pipeline(mock_load_config, mock_hmac, mock_json_dump, mock_train_model, mock_top_genres, mock_eda, mock_load_data):
    # Mock config
    mock_load_config.return_value = {
        'paths': {'input_data': 'dummy.csv'},
        'pipeline': {'top_genres_n': 2},
        'business_logic': {'success_multiplier': 2.5}
    }
    
    # Mock data loading
    mock_df = pd.DataFrame({
        'budget': [1000, 2000, 3000, 4000],
        'revenue': [2000, 4000, 6000, 8000],
        'popularity': [10.5, 20.1, 30.5, 40.1],
        'runtime': [90, 120, 100, 110],
        'vote_average': [6.5, 8.0, 7.5, 5.0],
        'success': [0, 1, 1, 0],
        'genre_list': [['Action'], ['Comedy'], ['Action'], ['Drama']]
    })
    mock_load_data.return_value = mock_df
    
    # Mock top genres
    mock_top_genres.return_value = ['Action', 'Comedy']
    
    # Mock HMAC
    mock_hmac.return_value = 'dummy_hmac'
    
    # Run the pipeline
    run_pipeline()
    
    # Assertions
    mock_load_data.assert_called_once()
    mock_eda.assert_called_once()
    mock_train_model.assert_called_once()
    assert mock_json_dump.call_count >= 1
