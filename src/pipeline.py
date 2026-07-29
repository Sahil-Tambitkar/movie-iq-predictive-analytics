import logging
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .preprocessor import load_and_clean_data
from .features import engineer_features, get_top_genres
from .models.predictive_model import train_and_save_model

logger = logging.getLogger(__name__)

def generate_eda_artifacts(df: pd.DataFrame) -> None:
    """Generate and save EDA plots."""
    logger.info("Generating EDA artifacts...")
    os.makedirs("assets", exist_ok=True)
    
    df_exploded = df.explode('genre_list')
    df_exploded = df_exploded[df_exploded['genre_list'].notna()]
    genre_counts = df_exploded['genre_list'].value_counts().head(10)
    
    # 1. Budget vs Revenue
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='budget', y='revenue', hue='success', alpha=0.6)
    plt.title('Budget vs Revenue')
    plt.tight_layout()
    plt.savefig('assets/budget_vs_revenue.png')
    plt.close()

    # 2. Top Genres
    plt.figure(figsize=(12, 6))
    sns.barplot(y=genre_counts.index, x=genre_counts.values, orient='h')
    plt.title('Top 10 Most Common Genres')
    plt.tight_layout()
    plt.savefig('assets/top_genres.png')
    plt.close()

    # 3. Features vs Success
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    sns.boxplot(data=df, x='success', y='popularity', ax=axes[0])
    sns.boxplot(data=df, x='success', y='runtime', ax=axes[1])
    sns.boxplot(data=df, x='success', y='vote_average', ax=axes[2])
    plt.tight_layout()
    plt.savefig('assets/features_vs_success.png')
    plt.close()

    # 4. Correlation Heatmap
    numeric_cols = ['budget', 'revenue', 'popularity', 'runtime', 'vote_average', 'success']
    plt.figure(figsize=(8, 6))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.tight_layout()
    plt.savefig('assets/correlation_heatmap.png')
    plt.close()

def run_pipeline() -> None:
    """Execute the full data pipeline: load, clean, split, EDA, feature engineer, and train."""
    from src.config_loader import load_config
    from datetime import datetime
    from sklearn.model_selection import train_test_split
    
    config = load_config()
    data_path = config['paths']['input_data']
    top_genres_n = config['pipeline']['top_genres_n']
    
    # Read the new business logic parameter
    success_multiplier = config.get('business_logic', {}).get('success_multiplier', 2.5)
    
    # Generate versioned paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs('artifacts/models', exist_ok=True)
    model_path = f"artifacts/models/model_{timestamp}.pkl"
    model_features_path = f"artifacts/models/model_features_{timestamp}.pkl"
    
    df = load_and_clean_data(data_path, success_multiplier=success_multiplier)
    
    # STRICT FIX: Perform train-test split BEFORE EDA to prevent Data Leakage!
    # We must not look at the test set during feature engineering or EDA.
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
    
    # Generate EDA only on the training set
    generate_eda_artifacts(df_train)
    
    # Determine top genres ONLY from the training set
    top_genres = get_top_genres(df_train, n=top_genres_n)
    
    # Apply feature engineering to both splits independently
    df_train_engineered = engineer_features(df_train.copy(), top_genres)
    df_test_engineered = engineer_features(df_test.copy(), top_genres)
    
    # Save Baseline Stats for UI (to avoid reloading CSV)
    successful_df = df_train[df_train['success'] == 1]
    baselines = {
        'budget': float(successful_df['budget'].mean()),
        'popularity': float(successful_df['popularity'].mean()),
        'vote_average': float(successful_df['vote_average'].mean()),
        'runtime': float(successful_df['runtime'].mean())
    }
    with open('artifacts/baseline_stats.json', 'w') as f:
        json.dump(baselines, f, indent=4)
    logger.info("Saved baseline statistics to artifacts/baseline_stats.json")
    
    # Define features
    features = ['budget', 'popularity', 'runtime', 'vote_average', 'word_of_mouth_ratio', 'hype_risk'] + [f'genre_{g}' for g in top_genres]
    
    # Target is now actual revenue (regression) rather than binary success
    X_train = df_train_engineered[features]
    y_train = df_train_engineered['revenue']
    
    X_test = df_test_engineered[features]
    y_test = df_test_engineered['revenue']
    
    # Train model safely
    train_and_save_model(
        X_train=X_train, 
        X_test=X_test, 
        y_train=y_train, 
        y_test=y_test, 
        features=features,
        model_path=model_path, 
        features_path=model_features_path
    )
    
    from src.utils import generate_file_hmac
    
    # Update metadata with new active model paths instead of modifying config.yaml
    metadata_path = os.path.join('artifacts', 'metadata.json')
    secret_key = os.environ.get('APP_SECRET_KEY', 'dev-key-123')
    metadata = {
        'model_path': model_path,
        'model_features_path': model_features_path,
        'model_hmac': generate_file_hmac(model_path, secret_key),
        'model_features_hmac': generate_file_hmac(model_features_path, secret_key)
    }
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    logger.info(f"Updated metadata.json with active model version: {timestamp}")

