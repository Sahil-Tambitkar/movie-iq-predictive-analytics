import streamlit as st
from src.preprocessor import load_and_clean_data, get_all_genres
from src.config_loader import load_config

def apply_global_styles():
    # Inject custom Google Fonts and CSS for premium neon-indigo styling
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        /* Sidebar Overrides */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #090d16 0%, #111827 100%);
            border-right: 1px solid rgba(139, 92, 246, 0.15);
        }
        
        /* Global Styles */
        .stApp {
            background: linear-gradient(135deg, #05070c 0%, #0c0f1d 100%);
            color: #e2e8f0;
        }
        
        /* Headers styling */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        
        .main-title {
            font-size: 2.8rem;
            background: linear-gradient(90deg, #38bdf8 0%, #a855f7 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.1rem;
            font-weight: 800;
        }
        
        /* Custom Card Style */
        .premium-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.75) 0%, rgba(30, 41, 59, 0.45) 100%);
            border: 1px solid rgba(139, 92, 246, 0.15);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(20px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 20px;
        }
        
        .premium-card:hover {
            transform: translateY(-5px);
            border-color: rgba(236, 72, 153, 0.4);
            box-shadow: 0 15px 35px rgba(139, 92, 246, 0.15);
        }
        
        .premium-card h3 {
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.35rem;
            color: #f8fafc;
        }
        
        /* Statistic box styling */
        .stat-val {
            font-size: 2.1rem;
            font-weight: 800;
            color: #f8fafc;
            margin-top: 5px;
            background: linear-gradient(90deg, #f8fafc 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-lbl {
            font-size: 0.8rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 600;
        }

        /* Glow buttons */
        div.stButton > button {
            background: linear-gradient(90deg, #0284c7 0%, #7c3aed 100%) !important;
            color: #ffffff !important;
            border: none !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.25) !important;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.45) !important;
            background: linear-gradient(90deg, #0ea5e9 0%, #8b5cf6 100%) !important;
        }

        /* Input focus styling */
        div[data-baseweb="input"] {
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
        }
        
        div[data-baseweb="input"]:focus-within {
            border-color: #38bdf8 !important;
        }
        
        /* Form */
        div[data-testid="stForm"] {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    config = load_config()
    df = load_and_clean_data(config['paths']['input_data'])
    all_genres = get_all_genres(df)
    return df, all_genres

def render_sidebar_filters(df, all_genres):
    st.sidebar.markdown("### 🎛️ Filter Parameters")
    
    selected_genres = st.sidebar.multiselect(
        "Select Genres", 
        options=all_genres, 
        default=all_genres[:3] if len(all_genres) >= 3 else all_genres
    )
    
    min_budget = int(df['budget'].min())
    max_budget = int(df['budget'].max())
    
    if min_budget == max_budget:
        budget_range = (min_budget, max_budget)
    else:
        budget_range = st.sidebar.slider(
            "Budget Range ($)", 
            min_value=min_budget, 
            max_value=max_budget, 
            value=(min_budget, max_budget),
            step=1000000,
            format="$%d"
        )
        
    min_rating = float(df['vote_average'].min()) if 'vote_average' in df.columns else 0.0
    max_rating = float(df['vote_average'].max()) if 'vote_average' in df.columns else 10.0
    rating_range = st.sidebar.slider(
        "Vote Average", 
        min_value=min_rating, 
        max_value=max_rating, 
        value=(min_rating, max_rating),
        step=0.1
    ) if min_rating != max_rating else (min_rating, max_rating)
    
    min_runtime = int(df['runtime'].min()) if 'runtime' in df.columns else 0
    max_runtime = int(df['runtime'].max()) if 'runtime' in df.columns else 300
    runtime_range = st.sidebar.slider(
        "Runtime (Minutes)", 
        min_value=min_runtime, 
        max_value=max_runtime, 
        value=(min_runtime, max_runtime),
        step=5
    ) if min_runtime != max_runtime else (min_runtime, max_runtime)
        
    filtered_df = df[
        (df['budget'] >= budget_range[0]) & 
        (df['budget'] <= budget_range[1])
    ]
    
    if 'vote_average' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['vote_average'] >= rating_range[0]) & 
            (filtered_df['vote_average'] <= rating_range[1])
        ]
        
    if 'runtime' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['runtime'] >= runtime_range[0]) & 
            (filtered_df['runtime'] <= runtime_range[1])
        ]
    
    if selected_genres:
        filtered_df = filtered_df[
            filtered_df['genre_list'].apply(lambda x: any(g in selected_genres for g in x))
        ]
        
    return filtered_df

import hmac
import hashlib

def generate_file_hmac(filepath: str, secret_key: str) -> str:
    """Generate a SHA256 HMAC for a given file."""
    h = hmac.new(secret_key.encode('utf-8'), digestmod=hashlib.sha256)
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def verify_file_hmac(filepath: str, expected_signature: str, secret_key: str) -> bool:
    """Verify the HMAC signature of a file."""
    actual_signature = generate_file_hmac(filepath, secret_key)
    return hmac.compare_digest(actual_signature, expected_signature)
