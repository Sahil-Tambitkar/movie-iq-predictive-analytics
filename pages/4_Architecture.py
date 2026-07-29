import streamlit as st
from src.utils import apply_global_styles

apply_global_styles()

st.header("ℹ️ About MovieIQ")
st.markdown("""
<div class='premium-card'>
    <h3 style='color:#38bdf8;'>Behind the Scenes</h3>
    <ul style='color:#cbd5e1;'>
        <li><b>Data Preparation</b>: Cleaned missing values and exploded nested JSON features.</li>
        <li><b>Modeling</b>: Utilized a Gradient Boosting Classifier achieving high accuracy by looking at Budget, Popularity, and Vote Averages. Optimized with SMOTE and GridSearchCV.</li>
        <li><b>Hybrid System</b>: Deployed an advanced architecture combining raw ML probabilities with an Expert System Overlay, allowing business heuristics (e.g., Sleeper Hits) to be safely applied on top of the data-driven model.</li>
        <li><b>Aesthetics</b>: Custom CSS styling with dynamic glassmorphism and modern dark mode visuals inspired by professional analytics hubs.</li>
        <li><b>Architecture</b>: Native Streamlit multi-page application with modularized backend pipeline (`src/`).</li>
    </ul>
</div>
""", unsafe_allow_html=True)
