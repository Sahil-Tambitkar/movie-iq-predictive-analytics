import pytest
import pandas as pd
from src.preprocessor import extract_genres, load_and_clean_data, get_all_genres

def test_extract_genres_valid():
    genres_str = "[{'id': 28, 'name': 'Action'}, {'id': 12, 'name': 'Adventure'}]"
    result = extract_genres(genres_str)
    assert result == ['Action', 'Adventure']

def test_extract_genres_invalid():
    assert extract_genres("") == []
    assert extract_genres(None) == []
    assert extract_genres("invalid json") == []

def test_get_all_genres():
    df = pd.DataFrame({'genre_list': [['Action', 'Adventure'], ['Action', 'Comedy']]})
    result = get_all_genres(df)
    assert sorted(result) == ['Action', 'Adventure', 'Comedy']

def test_load_and_clean_data(tmp_path):
    # Create a dummy CSV file
    df = pd.DataFrame({
        'budget': [1000, 0, 2000, 3000, 4000],
        'revenue': [2500, 2000, 0, 9000, 10000],
        'title': ['Movie A', 'Movie B', 'Movie C', '=Movie D', '+Movie E'],
        'genres': [
            "[{'id': 28, 'name': 'Action'}]",
            "[{'id': 12, 'name': 'Adventure'}]",
            "[{'id': 35, 'name': 'Comedy'}]",
            "[{'id': 18, 'name': 'Drama'}]",
            "[{'id': 878, 'name': 'Science Fiction'}]"
        ]
    })
    filepath = tmp_path / "dummy.csv"
    df.to_csv(filepath, index=False)
    
    # Test loading and cleaning
    cleaned_df = load_and_clean_data(str(filepath), success_multiplier=3.0)
    
    # Check that rows with 0 budget or 0 revenue were dropped
    assert len(cleaned_df) == 3
    
    # Check that strings starting with '=' or '+' were sanitized
    assert cleaned_df.iloc[1]['title'] == "'=Movie D"
    assert cleaned_df.iloc[2]['title'] == "'+Movie E"
    
    # Check success column (budget * 3.0)
    # Movie A: 1000 * 3 = 3000 -> revenue 2500 < 3000 (0)
    # Movie D: 3000 * 3 = 9000 -> revenue 9000 >= 9000 (1)
    # Movie E: 4000 * 3 = 12000 -> revenue 10000 < 12000 (0)
    assert list(cleaned_df['success']) == [0, 1, 0]

def test_load_and_clean_data_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_and_clean_data("non_existent_file.csv")
