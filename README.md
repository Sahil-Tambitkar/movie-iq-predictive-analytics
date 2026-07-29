# MovieIQ Predictive Analytics

MovieIQ is an AI-powered data science application that predicts the financial success of feature films based on pre-production logistics, sentiment, and genre analysis.

## Features
- **Data Engineering**: Cleans and imputes missing financial data, and engineers one-hot encoded genres.
- **Predictive Engine**: Uses an imbalanced learning pipeline (SMOTE + HistGradientBoostingClassifier) to forecast whether a movie will recoup 2.5x its budget.
- **Interactive Dashboard**: A multi-page Streamlit application with a premium UI for Exploratory Data Analysis, Model Evaluation, and real-time predictions.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/movieiq-predictive-analytics.git
   cd movieiq-predictive-analytics
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the source code as a local package:
   ```bash
   pip install -e .
   ```

## Usage

### 1. Train the Model
Before running the web app, you must execute the data pipeline to generate the EDA artifacts and train the model:
```bash
python build_models.py
```
*Note: This will safely update `artifacts/metadata.json` with the latest model paths.*

### 2. Run the Application
Launch the Streamlit dashboard:
```bash
python -m streamlit run app.py
```
Then navigate to `http://localhost:8501` in your browser.

## Testing
To run the automated unit tests:
```bash
pytest
```
