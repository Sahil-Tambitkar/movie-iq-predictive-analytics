import pandas as pd
import ast
import logging
from typing import List

logger = logging.getLogger(__name__)

def extract_genres(genre_str: str) -> List[str]:
    """Safely extract genre names from stringified JSON representations.
    
    Args:
        genre_str (str): A stringified JSON list of genre dictionaries.
        
    Returns:
        List[str]: A list of extracted genre names, or an empty list if parsing fails.
    """
    try:
        genres = ast.literal_eval(genre_str)
        return [g['name'] for g in genres]
    except (ValueError, SyntaxError, TypeError):
        return []

def load_and_clean_data(filepath: str, success_multiplier: float = 2.5) -> pd.DataFrame:
    """Load the dataset and execute the data cleaning pipeline.
    
    Args:
        filepath (str): The path to the CSV dataset.
        success_multiplier (float): The multiplier applied to budget to determine financial success.
        
    Returns:
        pd.DataFrame: The cleaned pandas DataFrame containing valid financial records.
        
    Raises:
        FileNotFoundError: If the dataset is not found at the specified path.
    """
    logger.info("Loading and cleaning data...")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        logger.error(f"Dataset not found at {filepath}")
        raise
        
    # 4. Missing Values Handling
    # Note: Numeric columns will be imputed during the pipeline after train-test split to avoid data leakage.
    

    # Text columns -> Fill with Mode or "Unknown"
    for col in ['title', 'genres']:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")
            
    # 5. Data Cleaning
    # Remove duplicate movies
    df.drop_duplicates(inplace=True)
    
    # Security: Sanitize strings to prevent CSV/Formula injection
    def sanitize_csv_string(val):
        if isinstance(val, str) and val.startswith(('=', '+', '-', '@')):
            return "'" + val
        return val
        
    df['title'] = df['title'].apply(sanitize_csv_string)
            
    # Check negative budget or revenue (filter out or ensure > 0)
    df = df[(df['budget'] > 0) & (df['revenue'] > 0)].copy()
    
    # Calculate success based on the configurable multiplier
    df['success'] = (df['revenue'] >= (df['budget'] * success_multiplier)).astype(int)
    
    # Extract genres and format them nicely to replace raw JSON
    df['genre_list'] = df['genres'].apply(lambda x: extract_genres(x) if x != "Unknown" else ["Unknown"])
    df['Genres'] = df['genre_list'].apply(lambda x: ", ".join(x))
    df.drop(columns=['genres'], inplace=True)
    
    return df

def get_all_genres(df: pd.DataFrame) -> List[str]:
    """Extract and compile a sorted list of all unique genres present in the dataset.
    
    Args:
        df (pd.DataFrame): The cleaned DataFrame containing a 'genre_list' column.
        
    Returns:
        List[str]: A sorted list of unique genre strings.
    """
    all_genres = set()
    for genres in df['genre_list']:
        all_genres.update(genres)
    return sorted(list(all_genres))
