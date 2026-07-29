import pandas as pd
from typing import List

def engineer_features(df: pd.DataFrame, top_genres: List[str]) -> pd.DataFrame:
    """Engineer features such as genre one-hot encodings based on a list of top genres.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing a 'genre_list' column.
        top_genres (List[str]): A list of genre strings to one-hot encode.
        
    Returns:
        pd.DataFrame: A new DataFrame with the added 'genre_{g}' binary indicator columns.
    """
    df_engineered = df.copy()
    for g in top_genres:
        # List comprehensions are significantly faster than .apply() for this operation
        df_engineered[f'genre_{g}'] = [1 if g in x else 0 for x in df_engineered['genre_list']]
        
    # Explicit Interaction Features for Word of Mouth & Hype
    # High rating but low popularity (Hidden Gem / Word of mouth momentum)
    # Adding a small epsilon (1) to popularity to avoid division by zero
    df_engineered['word_of_mouth_ratio'] = df_engineered['vote_average'] / (df_engineered['popularity'] + 1)
    
    # High popularity but terrible rating (Anticipated Flop / Hype Risk)
    df_engineered['hype_risk'] = df_engineered['popularity'] * (10 - df_engineered['vote_average'])
    
    return df_engineered

def get_top_genres(df: pd.DataFrame, n: int = 5) -> List[str]:
    """Identify the top `n` most frequent genres in the dataset.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing a 'genre_list' column.
        n (int, optional): The number of top genres to return. Defaults to 5.
        
    Returns:
        List[str]: A list of the top `n` most frequent genre names.
    """
    df_exploded = df.explode('genre_list')
    df_exploded = df_exploded[df_exploded['genre_list'].notna()]
    genre_counts = df_exploded['genre_list'].value_counts().head(n)
    return genre_counts.index.tolist()
