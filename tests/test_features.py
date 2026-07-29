import pytest
import pandas as pd
from src.features import engineer_features, get_top_genres

def test_get_top_genres():
    df = pd.DataFrame({'genre_list': [['Action'], ['Action'], ['Comedy'], ['Drama']]})
    result = get_top_genres(df, n=2)
    assert 'Action' in result
    assert len(result) == 2

def test_engineer_features():
    df = pd.DataFrame({
        'revenue': [150, 50],
        'budget': [100, 100],
        'success': [1, 0],
        'genre_list': [['Action'], ['Comedy']],
        'vote_average': [7.5, 4.0],
        'popularity': [80.0, 20.0]
    })
    
    top_genres = ['Action']
    df_engineered = engineer_features(df, top_genres)
    
    # Check OHE for top genres
    assert 'genre_Action' in df_engineered.columns
    assert df_engineered['genre_Action'].iloc[0] == 1
    assert df_engineered['genre_Action'].iloc[1] == 0
