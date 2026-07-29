import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.utils import apply_global_styles, load_data, render_sidebar_filters, generate_file_hmac, verify_file_hmac

@patch('src.utils.st.markdown')
def test_apply_global_styles(mock_markdown):
    apply_global_styles()
    mock_markdown.assert_called_once()

@patch('src.utils.load_config')
@patch('src.utils.load_and_clean_data')
@patch('src.utils.get_all_genres')
def test_load_data(mock_get_all_genres, mock_load_data, mock_load_config):
    # Mock data
    mock_load_config.return_value = {'paths': {'input_data': 'dummy.csv'}}
    mock_load_data.return_value = pd.DataFrame()
    mock_get_all_genres.return_value = ['Action']
    
    df, genres = load_data()
    assert df is not None
    assert genres == ['Action']

@patch('src.utils.st.sidebar')
def test_render_sidebar_filters(mock_sidebar):
    # Setup dataframe
    df = pd.DataFrame({
        'budget': [1000, 5000, 10000],
        'vote_average': [5.0, 7.5, 9.0],
        'runtime': [90, 120, 150],
        'genre_list': [['Action'], ['Comedy'], ['Action', 'Drama']]
    })
    
    # Mock sidebar outputs
    mock_sidebar.multiselect.return_value = ['Action']
    # Return full ranges to not filter out elements based on sliders
    mock_sidebar.slider.side_effect = [
        (1000, 10000),  # budget
        (5.0, 9.0),     # vote
        (90, 150)       # runtime
    ]
    
    filtered_df = render_sidebar_filters(df, ['Action', 'Comedy', 'Drama'])
    
    # Since we selected 'Action', we expect 2 rows (indices 0 and 2)
    assert len(filtered_df) == 2
    assert list(filtered_df.index) == [0, 2]

def test_render_sidebar_filters_same_budget():
    df = pd.DataFrame({
        'budget': [1000, 1000],
        'vote_average': [6.0, 6.0],
        'runtime': [100, 100],
        'genre_list': [['Action'], ['Action']]
    })
    with patch('src.utils.st.sidebar') as mock_sidebar:
        mock_sidebar.multiselect.return_value = []
        mock_sidebar.slider.side_effect = [(1000, 1000), (0, 10), (0, 200)]
        filtered = render_sidebar_filters(df, ['Action'])
        assert len(filtered) == 2

def test_generate_file_hmac(tmp_path):
    import os
    filepath = tmp_path / "test.txt"
    with open(filepath, "wb") as f:
        f.write(b"hello world")
        
    hmac_val = generate_file_hmac(str(filepath), "secret")
    assert isinstance(hmac_val, str)
    assert len(hmac_val) > 0

def test_verify_file_hmac(tmp_path):
    filepath = tmp_path / "test.txt"
    with open(filepath, "wb") as f:
        f.write(b"hello world")
        
    expected = generate_file_hmac(str(filepath), "secret")
    assert verify_file_hmac(str(filepath), expected, "secret") == True
    assert verify_file_hmac(str(filepath), "wrong_hmac", "secret") == False
