import streamlit as st
import os
from src.utils import apply_global_styles

st.set_page_config(page_title="Model Evaluation", page_icon="🧪", layout="wide")
apply_global_styles()
st.title("🧪 Model Evaluation & Metrics")
st.markdown("""
This section provides transparent, rigorous statistical evaluation of the predictive engine. A true data science project requires robust proof of performance beyond a simple accuracy score.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Classification Report")
    st.markdown("Detailed breakdown of precision, recall, and f1-score for both classes.")
    
    report_path = "assets/classification_report.txt"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            report_text = f.read()
        st.code(report_text, language="text")
    else:
        st.warning("Classification report not found. Run the training pipeline first.")

    st.subheader("Confusion Matrix")
    st.markdown("Visualizes exact predictions vs. reality to identify False Positives and False Negatives.")
    cm_path = "assets/confusion_matrix.png"
    if os.path.exists(cm_path):
        st.image(cm_path, use_container_width=True)
    else:
        st.warning("Confusion matrix not found.")

with col2:
    st.subheader("ROC-AUC Curve")
    st.markdown("Receiver Operating Characteristic curve. An AUC closer to 1.0 indicates excellent class separation capability.")
    roc_path = "assets/roc_curve.png"
    if os.path.exists(roc_path):
        st.image(roc_path, use_container_width=True)
    else:
        st.warning("ROC Curve not found.")
