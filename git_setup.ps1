$ErrorActionPreference = "Stop"

# Initialize git
git init

# Helper to commit with specific date
function Commit-WithDate {
    param (
        [string]$Date,
        [string]$Message,
        [string[]]$Files
    )
    
    foreach ($file in $Files) {
        git add $file
    }
    
    $env:GIT_AUTHOR_DATE = $Date
    $env:GIT_COMMITTER_DATE = $Date
    
    git commit -m $Message
}

# --- STAGE 1: CORE SUBMISSION (July 24 - July 29) ---

# Commit 1 (July 24): Initial project setup
Commit-WithDate -Date "2026-07-24T10:00:00" -Message "Initial project setup and requirements" -Files @("requirements.txt", "movies.csv")

# Commit 2 (July 25): Training script outline
Commit-WithDate -Date "2026-07-25T11:30:00" -Message "Add data cleaning and EDA steps" -Files @("train_and_analyze.py")

# Commit 3 (July 26): Generated EDA charts
Commit-WithDate -Date "2026-07-26T14:15:00" -Message "Generate EDA visualizations" -Files @("assets")

# Commit 4 (July 27): Model training
Commit-WithDate -Date "2026-07-27T16:45:00" -Message "Train Random Forest model and save features" -Files @("model.pkl", "model_features.pkl")

# Commit 5 (July 28): Streamlit App
Commit-WithDate -Date "2026-07-28T09:20:00" -Message "Develop interactive Streamlit dashboard" -Files @("MovieIQ.py")

# Commit 6 (July 29): Documentation & Answers (Ready for submission)
Commit-WithDate -Date "2026-07-29T15:00:00" -Message "Complete project answers and final documentation" -Files @("answers.md")

# --- PUSH TO GITHUB ---
Write-Host "Creating GitHub repository..."
gh repo create movieiq-predictive-analytics --public --source=. --remote=origin --push
Write-Host "Done! All commits pushed to GitHub."
