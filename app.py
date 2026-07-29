import streamlit as st

# Configuration
st.set_page_config(
    page_title="MovieIQ Dashboard", 
    page_icon="🎬", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Robust Navigation setup
pages = {
    "Dashboard": [
        st.Page("pages/0_Dashboard.py", title="Dashboard Home", icon="🏠", default=True),
    ],
    "Analytics & Engine": [
        st.Page("pages/1_EDA.py", title="Exploratory Data Analysis", icon="📈"),
        st.Page("pages/3_Model_Evaluation.py", title="Model Evaluation", icon="🧪"),
        st.Page("pages/2_Predictive_Engine.py", title="Predictive Engine", icon="🤖"),
        st.Page("pages/4_Architecture.py", title="Architecture", icon="ℹ️")
    ]
}
pg = st.navigation(pages)
pg.run()
