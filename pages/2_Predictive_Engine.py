import streamlit as st
import pandas as pd
import joblib
import json
import os
from src.config_loader import load_config
from src.utils import apply_global_styles

apply_global_styles()

st.header("🔮 Predictive Engine")
st.markdown("""
This engine utilizes the core metrics available in the dataset (Budget, Runtime, Popularity, Vote Average, and Genre) to forecast the actual box office revenue.
""")

try:
    config = load_config()
    # SECURITY WARNING: joblib.load uses pickle under the hood, which can execute arbitrary code.
    # NEVER load models uploaded by users. Only load from the trusted local paths defined in config.
    
    # HMAC VERIFICATION
    from src.utils import verify_file_hmac
    secret_key = os.environ.get('APP_SECRET_KEY', 'dev-key-123')
    
    if config.get('model_hmac'):
        if not verify_file_hmac(config['paths']['model'], config['model_hmac'], secret_key):
            st.error("SECURITY ALERT: Model file integrity check failed. Possible tampering detected. Refusing to load.")
            st.stop()
            
    if config.get('model_features_hmac'):
        if not verify_file_hmac(config['paths']['model_features'], config['model_features_hmac'], secret_key):
            st.error("SECURITY ALERT: Model features file integrity check failed. Possible tampering detected. Refusing to load.")
            st.stop()

    model = joblib.load(config['paths']['model'])
    model_features = joblib.load(config['paths']['model_features'])
except Exception as e:
    st.error(f"Model error: {str(e)}. Please run the training script first.")
    st.stop()
    
numeric_features = [f for f in model_features if not f.startswith('genre_')]
top_genres = [f.replace('genre_', '') for f in model_features if f.startswith('genre_')]

st.markdown("##### 🔢 Pre-Production Financials & Logistics")
inputs = {}
cols = st.columns(2)

for i, feature in enumerate(numeric_features):
    if feature in ['word_of_mouth_momentum', 'word_of_mouth_ratio', 'hype_risk']:
        continue
    
    col = cols[i % 2]
    if 'budget' in feature.lower():
        inputs[feature] = col.number_input(feature.capitalize() + " ($)", min_value=1000, value=5000000, step=1000000)
    elif 'popularity' in feature.lower():
        inputs[feature] = col.slider(feature.capitalize(), min_value=0.0, max_value=200.0, value=50.0, step=1.0)
    elif 'vote' in feature.lower():
        inputs[feature] = col.slider(feature.capitalize() + " (0-10)", min_value=0.0, max_value=10.0, value=6.5, step=0.1)
    elif 'runtime' in feature.lower():
        inputs[feature] = col.number_input(feature.capitalize() + " (minutes)", min_value=1, value=100, step=5)
    else:
        inputs[feature] = col.number_input(feature.replace('_', ' ').capitalize(), value=0.0)
        
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("##### 🎭 Select Core Genres")
genre_selections = {}

if top_genres:
    genre_cols = st.columns(min(len(top_genres), 4))
    for i, g in enumerate(top_genres):
        with genre_cols[i % 4]:
            genre_selections[g] = st.checkbox(g, value=True if i==0 else False) # Default first genre to true so it predicts immediately
            
st.markdown("<hr>", unsafe_allow_html=True)

# Validate that at least one genre is selected
if not any(genre_selections.values()):
    st.info("ℹ️ Please select at least one genre to see the prediction.")
else:
    # Construct input dataframe dynamically matching model features
    input_data = inputs.copy()
    
    # Calculate engineered interaction features
    popularity = inputs.get('popularity', 50.0)
    vote_average = inputs.get('vote_average', 6.5)
    input_data['word_of_mouth_ratio'] = vote_average / (popularity + 1)
    input_data['hype_risk'] = popularity * (10 - vote_average)
    
    for g in top_genres:
        input_data[f'genre_{g}'] = 1 if genre_selections.get(g, False) else 0
        
    input_df = pd.DataFrame([input_data])[model_features]
    
    # Get the raw regression prediction (predicted revenue)
    predicted_revenue = model.predict(input_df)[0]
    # Ensure revenue doesn't predict negative
    predicted_revenue = max(0, predicted_revenue)
    
    # ---------------------------------------------------------
    # EXPLICIT BUSINESS LOGIC OVERRIDES
    # ---------------------------------------------------------
    # 1. The "Anticipated Flop" Penalty: High hype, terrible word of mouth
    if popularity > 80.0 and vote_average < 5.0:
        predicted_revenue = predicted_revenue * 0.3
        st.warning("⚠️ **Business Override Applied:** Anticipated Flop Penalty (-70%) due to massive Hype but terrible Word of Mouth.")
        
    # 2. The "Word of Mouth Momentum" Boost: Low hype, incredible word of mouth
    elif popularity < 30.0 and vote_average > 7.5:
        predicted_revenue = predicted_revenue * 3.0
        st.success("📈 **Business Override Applied:** Sleeper Hit Boost (+200%) due to incredible Word of Mouth despite low Hype.")
    # ---------------------------------------------------------
    
    budget = inputs.get('budget', 0)
    success_multiplier = config.get('business_logic', {}).get('success_multiplier', 2.5)
    target_revenue = budget * success_multiplier
    
    prediction_is_success = predicted_revenue >= target_revenue
    roi = predicted_revenue / budget if budget > 0 else 0
    
    st.markdown("### 📊 Revenue Prediction Results")
    
    st.markdown(f"- **Predicted Box Office Revenue:** `${predicted_revenue:,.0f}`")
    st.markdown(f"- **Estimated ROI:** `{roi:.2f}x`")
    st.markdown(f"- **Required Revenue for Success ({success_multiplier}x multiplier):** `${target_revenue:,.0f}`")
    
    if prediction_is_success:
        st.markdown(f"""
        <div style='background-color: rgba(16, 185, 129, 0.15); border-left: 4px solid #10b981; padding: 15px; border-radius: 8px; margin-top: 15px;'>
            <h3 style='color: #10b981; margin: 0;'>🎉 Prediction: FINANCIAL SUCCESS</h3>
            <p style='color: #f8fafc; margin: 5px 0 0 0;'>The model predicts this film will cross the profitability threshold of ${target_revenue:,.0f}.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color: rgba(239, 68, 68, 0.15); border-left: 4px solid #ef4444; padding: 15px; border-radius: 8px; margin-top: 15px;'>
            <h3 style='color: #ef4444; margin: 0;'>📉 Prediction: BOX OFFICE BOMB (FAILURE)</h3>
            <p style='color: #f8fafc; margin: 5px 0 0 0;'>The model predicts this film will fail to reach the profitability threshold of ${target_revenue:,.0f}.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### 📊 Model Explainability: Input vs Baseline")
    
    import plotly.express as px
    
    # Load Baseline stats instead of loading entire CSV
    baseline_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts', 'baseline_stats.json')
    try:
        with open(baseline_path, 'r') as f:
            baselines = json.load(f)
    except Exception as e:
        st.warning("Baseline statistics not found. Please re-run the training pipeline.")
        baselines = {'budget': budget, 'popularity': inputs.get('popularity', 50), 'vote_average': inputs.get('vote_average', 6.5), 'runtime': inputs.get('runtime', 100)}
    
    diffs = {
        'Budget': (inputs.get('budget', 0) - baselines['budget']) / baselines['budget'] * 100 if baselines['budget'] else 0,
        'Popularity': (inputs.get('popularity', 0) - baselines['popularity']) / baselines['popularity'] * 100 if baselines['popularity'] else 0,
        'Vote Average': (inputs.get('vote_average', 0) - baselines['vote_average']) / baselines['vote_average'] * 100 if baselines['vote_average'] else 0,
        'Runtime': (inputs.get('runtime', 0) - baselines['runtime']) / baselines['runtime'] * 100 if baselines['runtime'] else 0
    }
    
    diff_df = pd.DataFrame(list(diffs.items()), columns=['Feature', '% Difference from Successful Average'])
    diff_df['Color'] = diff_df['% Difference from Successful Average'].apply(lambda x: 'Above Baseline' if x > 0 else 'Below Baseline')

    fig_exp = px.bar(
        diff_df, x='% Difference from Successful Average', y='Feature', orientation='h', color='Color',
        color_discrete_map={'Above Baseline': '#10b981', 'Below Baseline': '#ef4444'},
        title="Your Film vs Average Successful Film"
    )
    fig_exp.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_exp, use_container_width=True)


