import streamlit as st
import plotly.express as px
from src.utils import load_data, render_sidebar_filters, apply_global_styles

apply_global_styles()

try:
    df, all_genres = load_data()
except Exception as e:
    st.error(f"Error loading data. Ensure movies.csv is present in the directory. Error: {e}")
    st.stop()

filtered_df = render_sidebar_filters(df, all_genres)

# Header banner
st.markdown("""
<div style='background: linear-gradient(135deg, #1e1b4b 0%, #311042 50%, #0f172a 100%); padding: 22px 28px; border-radius: 18px; margin-bottom: 25px; border: 1px solid rgba(139, 92, 246, 0.25); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);'>
    <h1 style='margin: 0; font-size: 2rem; color: #ffffff;' class='main-title'>MovieIQ Predictive Analytics</h1>
    <p style='margin: 5px 0 0 0; color: #cbd5e1; font-size: 0.95rem; font-weight: 300;'>AI-Powered Film Success Forecasting & Market Analysis</p>
</div>
""", unsafe_allow_html=True)

# Top Level KPIs using premium cards
c1, c2, c3, c4 = st.columns(4)
total_movies = len(filtered_df)
global_total = len(df)

if total_movies > 0:
    success_rate = (filtered_df['success'].sum() / total_movies) * 100
    avg_budget = filtered_df['budget'].mean() / 1e6
    avg_revenue = filtered_df['revenue'].mean() / 1e6
else:
    success_rate = 0.0
    avg_budget = 0.0
    avg_revenue = 0.0

if global_total > 0:
    g_success_rate = (df['success'].sum() / global_total) * 100
    g_avg_budget = df['budget'].mean() / 1e6
    g_avg_revenue = df['revenue'].mean() / 1e6
else:
    g_success_rate, g_avg_budget, g_avg_revenue = 0.0, 0.0, 0.0

d_movies = total_movies - global_total
d_success = success_rate - g_success_rate
d_budget = avg_budget - g_avg_budget
d_revenue = avg_revenue - g_avg_revenue

def get_delta_html(val, is_pct=False, is_currency=False):
    color = "#10b981" if val >= 0 else "#ef4444"
    arrow = "▲" if val >= 0 else "▼"
    abs_val = abs(val)
    if is_pct:
        text = f"{abs_val:.1f}%"
    elif is_currency:
        text = f"${abs_val:.1f}M"
    else:
        text = f"{int(abs_val):,}"
    return f"<div style='font-size:0.85rem; color:{color}; margin-top:5px; font-weight:600;'>{arrow} {text} vs Global</div>"

with c1:
    st.markdown(f"<div class='premium-card'><div class='stat-lbl'>Filtered Movies</div><div class='stat-val'>{total_movies:,}</div>{get_delta_html(d_movies)}</div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='premium-card'><div class='stat-lbl'>Filtered Success Rate</div><div class='stat-val'>{success_rate:.1f} <span style='font-size:0.9rem;color:#10b981;font-weight:600;'>%</span></div>{get_delta_html(d_success, is_pct=True)}</div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='premium-card'><div class='stat-lbl'>Average Budget</div><div class='stat-val'>${avg_budget:.1f}M</div>{get_delta_html(d_budget, is_currency=True)}</div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='premium-card'><div class='stat-lbl'>Average Revenue</div><div class='stat-val'>${avg_revenue:.1f}M</div>{get_delta_html(d_revenue, is_currency=True)}</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_table, col_chart = st.columns([1.1, 0.9])

with col_table:
    st.markdown("### 📋 Top Genres Summary")
    df_exploded = filtered_df.explode('genre_list')
    genre_summary = df_exploded.groupby('genre_list').agg(
        Count=('title', 'count'),
        Avg_Budget=('budget', 'mean'),
        Avg_Revenue=('revenue', 'mean'),
        Success_Rate=('success', 'mean')
    ).sort_values('Count', ascending=False).head(5).reset_index()
    
    genre_summary['Success_Rate'] = genre_summary['Success_Rate'] * 100
    genre_summary = genre_summary.rename(columns={'genre_list': 'Genre'})
    
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Filtered Data (CSV)",
        data=csv_data,
        file_name="movie_iq_filtered_data.csv",
        mime="text/csv"
    )
    
    event = st.dataframe(
        genre_summary, 
        use_container_width=True, 
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        column_config={
            "Genre": st.column_config.TextColumn("Genre", width="medium"),
            "Count": st.column_config.NumberColumn("Movies Count", format="%d"),
            "Avg_Budget": st.column_config.NumberColumn("Avg Budget", format="$%.0f"),
            "Avg_Revenue": st.column_config.NumberColumn("Avg Revenue", format="$%.0f"),
            "Success_Rate": st.column_config.ProgressColumn(
                "Success Rate",
                format="%.1f%%",
                min_value=0,
                max_value=100
            )
        }
    )
    
    st.markdown("""
    <div class='premium-card' style='margin-top: 15px;'>
        <h4 style='color:#38bdf8; margin-top:0;'>💡 Executive Summary</h4>
        <p style='color:#94a3b8; font-size:0.95rem; line-height:1.6; margin-bottom:0;'>
            Welcome to the <b>MovieIQ Hub</b>. The table above outlines the performance of the most commonly produced movie genres. Use the sidebar to navigate to the deep <b>Exploratory Data Analysis</b> or the live <b>Predictive Engine</b> to forecast success.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
with col_chart:
    st.markdown("### 📊 Success Rate by Top Genres")
    
    # Check if rows are selected in the dataframe
    selected_indices = event.selection.rows if hasattr(event, "selection") and hasattr(event.selection, "rows") else []
    
    if selected_indices:
        # Filter chart to only selected genres
        selected_genres = genre_summary.iloc[selected_indices]['Genre'].tolist()
        genre_summary_chart = df_exploded[df_exploded['genre_list'].isin(selected_genres)].groupby('genre_list').agg(
            Success_Rate=('success', 'mean')
        ).sort_values('Success_Rate', ascending=False).reset_index()
    else:
        # Show top 5 default
        genre_summary_chart = df_exploded.groupby('genre_list').agg(
            Success_Rate=('success', 'mean')
        ).sort_values('Success_Rate', ascending=False).head(5).reset_index()
        
    genre_summary_chart['Success_Rate'] = genre_summary_chart['Success_Rate'] * 100
    
    fig_bar = px.bar(
        genre_summary_chart, x='genre_list', y='Success_Rate', color='genre_list',
        text='Success_Rate', color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_bar.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, margin=dict(l=10, r=10, t=10, b=10)
    )
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

