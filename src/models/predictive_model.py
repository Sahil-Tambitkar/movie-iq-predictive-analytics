import pandas as pd
import logging
import joblib
from typing import List
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import os
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import numpy as np

logger = logging.getLogger(__name__)

def train_and_save_model(
    X_train: pd.DataFrame, 
    X_test: pd.DataFrame, 
    y_train: pd.Series, 
    y_test: pd.Series, 
    features: List[str], 
    model_path: str = 'model.pkl', 
    features_path: str = 'model_features.pkl'
) -> None:
    """Train the Gradient Boosting Regressor using GridSearchCV, then save artifacts.
    
    Args:
        X_train (pd.DataFrame): Training feature set.
        X_test (pd.DataFrame): Testing feature set.
        y_train (pd.Series): Training target labels (revenue).
        y_test (pd.Series): Testing target labels (revenue).
        features (List[str]): List of feature names used for training.
        model_path (str): Path to save the trained model.
        features_path (str): Path to save the feature list.
    """
    logger.info("Training regression model with GridSearchCV...")
    
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('gb', HistGradientBoostingRegressor(random_state=42))
    ])
    
    # Define parameter grid for GridSearchCV (note the 'gb__' prefix for pipeline)
    param_grid = {
        'gb__learning_rate': [0.05, 0.1],
        'gb__max_iter': [50, 100],
        'gb__max_depth': [5, 10]
    }
    
    grid_search = GridSearchCV(estimator=pipeline, param_grid=param_grid, cv=3, n_jobs=None, scoring='neg_mean_absolute_error')
    grid_search.fit(X_train, y_train)
    
    best_pipeline = grid_search.best_estimator_
    logger.info(f"Best parameters found: {grid_search.best_params_}")
    
    preds_log = best_pipeline.predict(X_test)
    
    # Transform predictions and actuals back to original dollar scale for interpretable metrics
    preds = np.expm1(preds_log)
    y_test_dollars = np.expm1(y_test)
    
    mae = mean_absolute_error(y_test_dollars, preds)
    rmse = np.sqrt(mean_squared_error(y_test_dollars, preds))
    r2 = r2_score(y_test_dollars, preds)

    
    logger.info(f"Model MAE: ${mae:,.2f}")
    logger.info(f"Model RMSE: ${rmse:,.2f}")
    logger.info(f"Model R2: {r2:.4f}")
    
    # Generate Advanced Evaluation Metrics
    os.makedirs("assets", exist_ok=True)
    
    # 1. Actual vs Predicted Scatter Plot
    plt.figure(figsize=(7, 6))
    plt.scatter(y_test_dollars, preds, alpha=0.5, color='blue', edgecolor='k')
    plt.plot([y_test_dollars.min(), y_test_dollars.max()], [y_test_dollars.min(), y_test_dollars.max()], 'r--', lw=2)
    plt.xlabel('Actual Revenue')
    plt.ylabel('Predicted Revenue')
    plt.title(f'Actual vs Predicted Revenue (R2: {r2:.2f})')
    plt.tight_layout()
    plt.savefig('assets/actual_vs_predicted.png')
    plt.close()
    
    # 2. Residual Plot
    residuals = y_test_dollars - preds
    plt.figure(figsize=(7, 6))
    plt.scatter(preds, residuals, alpha=0.5, color='purple', edgecolor='k')
    plt.axhline(0, color='r', linestyle='--', lw=2)
    plt.xlabel('Predicted Revenue')
    plt.ylabel('Residuals (Actual - Predicted)')
    plt.title('Residual Plot')
    plt.tight_layout()
    plt.savefig('assets/residual_plot.png')
    plt.close()
    
    # 3. Regression Report text
    report = (
        f"Regression Metrics on Test Set:\n"
        f"---------------------------------\n"
        f"Mean Absolute Error (MAE): ${mae:,.2f}\n"
        f"Root Mean Squared Error (RMSE): ${rmse:,.2f}\n"
        f"R-squared (R2): {r2:.4f}\n"
    )
    with open('assets/regression_report.txt', 'w') as f:
        f.write(report)
        
    logger.info("Evaluation metrics generated and saved to assets/")
    
    joblib.dump(best_pipeline, model_path)
    joblib.dump(features, features_path)
    logger.info("Model and features saved successfully.")
