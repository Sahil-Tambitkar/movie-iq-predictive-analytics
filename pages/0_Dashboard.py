import streamlit as st
import plotly.express as px
import pandas as pd
from src.utils import load_data, render_sidebar_filters, apply_global_styles

apply_global_styles()

try:
    df, all_genres = load_data()
except Exception as e:
    st.error(f"Error loading data. Ensure movies.csv is present in the directory. Error: {e}")
    st.stop()

# 1. Project Title
st.markdown("""
<div style='background: linear-gradient(135deg, #1e1b4b 0%, #311042 50%, #0f172a 100%); padding: 22px 28px; border-radius: 18px; margin-bottom: 25px; border: 1px solid rgba(139, 92, 246, 0.25); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);'>
    <h1 style='margin: 0; font-size: 2rem; color: #ffffff;' class='main-title'>Movie Revenue Analysis Dashboard</h1>
    <p style='margin: 5px 0 0 0; color: #cbd5e1; font-size: 0.95rem; font-weight: 300;'>Explore what makes a movie successful</p>
</div>
""", unsafe_allow_html=True)

# 2. Sidebar
filtered_df = render_sidebar_filters(df, all_genres)

# 4. KPI Cards
total_movies = len(filtered_df)
avg_revenue = filtered_df['revenue'].mean() if total_movies > 0 else 0
avg_budget = filtered_df['budget'].mean() if total_movies > 0 else 0
avg_rating = filtered_df['vote_average'].mean() if total_movies > 0 and 'vote_average' in filtered_df else 0

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"<div class='premium-card'><div class='stat-lbl'>Total Movies</div><div class='stat-val'>{total_movies:,}</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='premium-card'><div class='stat-lbl'>Average Revenue</div><div class='stat-val'>${avg_revenue/1e6:.1f}M</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='premium-card'><div class='stat-lbl'>Average Budget</div><div class='stat-val'>${avg_budget/1e6:.1f}M</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='premium-card'><div class='stat-lbl'>Average Rating</div><div class='stat-val'>{avg_rating:.1f} / 10</div></div>", unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# 3. Dataset Preview
st.subheader("Dataset Preview")
st.dataframe(filtered_df.head(100), use_container_width=True)

st.markdown("<hr/>", unsafe_allow_html=True)

# 5. Interactive Charts
st.subheader("Interactive Charts")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Top 10 Revenue Movies
    st.markdown("#### Top 10 Revenue Movies")
    top_10 = filtered_df.nlargest(10, 'revenue')
    fig1 = px.bar(top_10, x='revenue', y='title', orientation='h', color='revenue', title="Top 10 Revenue Movies")
    fig1.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    # Revenue by Genre
    st.markdown("#### Revenue by Genre")
    df_exploded = filtered_df.explode('genre_list')
    genre_rev = df_exploded.groupby('genre_list')['revenue'].mean().reset_index().sort_values('revenue', ascending=False)
    fig2 = px.bar(genre_rev.head(10), x='genre_list', y='revenue', color='revenue', title="Average Revenue by Genre (Top 10)")
    st.plotly_chart(fig2, use_container_width=True)

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    # Budget vs Revenue
    st.markdown("#### Budget vs Revenue")
    fig3 = px.scatter(filtered_df, x='budget', y='revenue', color='vote_average', hover_data=['title'], title="Budget vs Revenue")
    st.plotly_chart(fig3, use_container_width=True)

with chart_col4:
    # Popularity vs Revenue
    st.markdown("#### Popularity vs Revenue")
    if 'popularity' in filtered_df.columns:
        fig4 = px.scatter(filtered_df, x='popularity', y='revenue', color='vote_average', hover_data=['title'], title="Popularity vs Revenue")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Popularity column not available.")

chart_col5, chart_col6 = st.columns(2)

with chart_col5:
    # Runtime Distribution
    st.markdown("#### Runtime Distribution")
    if 'runtime' in filtered_df.columns:
        fig5 = px.histogram(filtered_df, x='runtime', nbins=30, title="Runtime Distribution", color_discrete_sequence=['#38bdf8'])
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Runtime column not available.")

with chart_col6:
    # Rating Distribution
    st.markdown("#### Rating Distribution")
    if 'vote_average' in filtered_df.columns:
        fig6 = px.histogram(filtered_df, x='vote_average', nbins=30, title="Rating Distribution", color_discrete_sequence=['#a855f7'])
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Vote Average column not available.")

st.markdown("<hr/>", unsafe_allow_html=True)

# 6. Business Insights
st.subheader("Business Insights")
st.markdown("""
<div class='premium-card'>
    <ul>
        <li><b>Action and Adventure</b> movies consistently generate the highest average revenue, likely due to wide international appeal.</li>
        <li><b>High-budget movies</b> often earn more revenue, showing a strong positive correlation in the Budget vs Revenue chart.</li>
        <li>However, some <b>low-budget movies</b> (like certain horror or indie films) also achieve massive success and high ROI.</li>
        <li><b>Popular movies</b> generally translate to higher revenue, as seen in the clear trend between popularity score and box office earnings.</li>
        <li><b>Highly rated movies</b> attract audiences, leading to longer theatrical runs and solid financial performance.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 7. Business Recommendations
st.subheader("Business Recommendations")
st.markdown("""
<div class='premium-card' style='border-color: #10b981;'>
    <ul>
        <li><b>Invest more in profitable genres:</b> Focus production on Action, Adventure, and Sci-Fi if the goal is maximizing total box office revenue.</li>
        <li><b>Plan budgets based on historical performance:</b> Reserve high budgets ($100M+) for established, widely appealing concepts and franchises.</li>
        <li><b>Improve marketing for high audience interest:</b> Popularity is strongly linked to revenue; prioritize aggressive pre-release marketing campaigns.</li>
        <li><b>Study successful low-budget movies:</b> Emulate the creative and marketing models of high-ROI low-budget films to diversify risk.</li>
        <li><b>Focus on genres with consistently good ratings:</b> High ratings correlate with steady box office and strong streaming/VOD performance over time.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
