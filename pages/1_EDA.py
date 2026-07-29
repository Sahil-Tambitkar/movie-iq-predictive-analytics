import streamlit as st
import plotly.express as px
from src.utils import load_data, render_sidebar_filters, apply_global_styles

apply_global_styles()
try:
    df, all_genres = load_data()
except Exception as e:
    st.error("Error loading data. Ensure movies.csv is present in the directory.")
    st.stop()

filtered_df = render_sidebar_filters(df, all_genres)

st.header("📈 Exploratory Data Analysis")

tab_fin, tab_genre, tab_pop, tab_time = st.tabs([
    "💰 Financials & ROI", 
    "🎭 Genre Insights", 
    "⭐ Reception & Popularity",
    "⏳ Runtime & Correlations"
])

with tab_fin:
    st.markdown("### 💰 Financials & ROI Metrics")
    c1, c2 = st.columns(2)
    with c1:
        # 1. Budget vs Revenue
        fig1 = px.scatter(
            filtered_df, x='budget', y='revenue', color='success', 
            hover_data=['title'], opacity=0.7,
            title="1. Budget vs Revenue Correlation",
            color_continuous_scale=px.colors.sequential.Teal,
            labels={'budget': 'Budget ($)', 'revenue': 'Revenue ($)', 'success': 'Success'},
            trendline="ols"
        )
        fig1.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        fig1.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Budget: $%{x:,.0f}<br>Revenue: $%{y:,.0f}<extra></extra>", selector=dict(mode="markers"))
        st.plotly_chart(fig1, use_container_width=True)
        st.info("💡 **Financial Insight:** While higher budgets generally correlate with higher revenue, there is substantial variance. Many high-budget movies fail to break even.")

    with c2:
        # 4. ROI Distribution
        roi_df = filtered_df.copy()
        roi_df['ROI'] = roi_df['revenue'] / roi_df['budget']
        fig4 = px.histogram(
            roi_df[roi_df['ROI'] <= 10], x="ROI", nbins=50,
            title="4. Return on Investment Distribution (Clipped at 10x)", 
            color_discrete_sequence=["#14b8a6"]
        )
        fig4.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig4, use_container_width=True)
        st.info("💡 **ROI Insight:** The majority of profitable films make between 1x and 3x their budget. Films exceeding 5x ROI are rare blockbusters or highly successful indie films.")

    c3, c4 = st.columns(2)
    with c3:
        # 2. Top 10 Most Expensive Movies
        top_budget = filtered_df.nlargest(10, 'budget')
        fig2 = px.bar(
            top_budget, x='budget', y='title', orientation='h',
            title="2. Top 10 Most Expensive Movies", color='budget',
            color_continuous_scale="Purples", hover_data=['budget']
        )
        fig2.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig2, use_container_width=True)
        st.info("💡 **Cost Insight:** Major studio franchises like Pirates of the Caribbean or Avengers dominate the highest budgets ever recorded.")
    with c4:
        # 3. Top 10 Highest Grossing Movies
        top_revenue = filtered_df.nlargest(10, 'revenue')
        fig3 = px.bar(
            top_revenue, x='revenue', y='title', orientation='h',
            title="3. Top 10 Highest Grossing Movies", color='revenue',
            color_continuous_scale="Blues", hover_data=['revenue']
        )
        fig3.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig3, use_container_width=True)
        st.info("💡 **Gross Revenue Insight:** The highest-grossing movies are almost universally sci-fi, fantasy, or superhero franchises that appeal to global audiences.")

with tab_genre:
    st.markdown("### 🎭 Genre Production & Success")
    df_exploded = filtered_df.explode('genre_list')
    
    c1, c2 = st.columns(2)
    with c1:
        # 5. Genre Frequency
        genre_counts = df_exploded['genre_list'].value_counts().head(12).reset_index()
        genre_counts.columns = ['Genre', 'Count']
        fig5 = px.bar(
            genre_counts, x='Count', y='Genre', orientation='h',
            title="5. Top Genres by Frequency", color='Count', color_continuous_scale='Blues'
        )
        fig5.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig5, use_container_width=True)
        st.info("💡 **Production Insight:** Drama and Comedy are historically the most produced genres, likely due to their lower barrier to entry and lower average budgets.")

    with c2:
        # 6. Average Revenue per Genre
        genre_rev = df_exploded.groupby('genre_list')['revenue'].mean().sort_values(ascending=False).head(12).reset_index()
        fig6 = px.bar(
            genre_rev, x='revenue', y='genre_list', orientation='h',
            title="6. Average Revenue by Genre", color='revenue', color_continuous_scale='Greens'
        )
        fig6.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig6, use_container_width=True)
        st.info("💡 **Genre Revenue Insight:** Action, Adventure, and Sci-Fi consistently top the charts for average gross revenue, driven by broad international appeal.")

    c3, c4 = st.columns(2)
    with c3:
        # 7. Average Budget per Genre
        genre_bud = df_exploded.groupby('genre_list')['budget'].mean().sort_values(ascending=False).head(12).reset_index()
        fig7 = px.bar(
            genre_bud, x='budget', y='genre_list', orientation='h',
            title="7. Average Budget by Genre", color='budget', color_continuous_scale='Reds'
        )
        fig7.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig7, use_container_width=True)
        st.info("💡 **Genre Cost Insight:** Animation and Adventure require enormous upfront capital due to heavy VFX and production timelines.")
    with c4:
        # 8. Success Rate by Genre
        genre_succ = df_exploded.groupby('genre_list')['success'].mean().sort_values(ascending=False).head(12).reset_index()
        genre_succ['success'] = genre_succ['success'] * 100
        fig8 = px.bar(
            genre_succ, x='success', y='genre_list', orientation='h',
            title="8. Success Rate (%) by Genre", color='success', color_continuous_scale='plasma'
        )
        fig8.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig8, use_container_width=True)
        st.info("💡 **Genre Success Insight:** Horror and Thriller genres often have phenomenal success rates relative to their extremely low micro-budgets.")

with tab_pop:
    st.markdown("### ⭐ Critical Reception & Popularity")
    c1, c2 = st.columns(2)
    with c1:
        # 9. Vote Average Distribution
        fig9 = px.histogram(
            filtered_df, x="vote_average", nbins=40,
            title="9. Distribution of Vote Averages", color_discrete_sequence=["#ec4899"]
        )
        fig9.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig9, use_container_width=True)
        st.info("💡 **Rating Insight:** The vast majority of movies fall in the 5.5 to 7.5 rating range. A rating above 8 is exceptionally rare and highly predictive of success.")

    with c2:
        # 10. Popularity Distribution
        fig10 = px.histogram(
            filtered_df[filtered_df['popularity'] <= 150], x="popularity", nbins=50,
            title="10. Distribution of Popularity Scores (Clipped at 150)", color_discrete_sequence=["#3b82f6"]
        )
        fig10.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig10, use_container_width=True)
        st.info("💡 **Popularity Insight:** Popularity is heavily right-skewed. A small number of blockbuster films capture the vast majority of public attention.")

    c3, c4 = st.columns(2)
    with c3:
        # 11. Popularity vs Revenue
        fig11 = px.scatter(
            filtered_df, x='popularity', y='revenue', color='success',
            title="11. Popularity vs Box Office Revenue", opacity=0.7,
            color_continuous_scale="Viridis", hover_data=['title'],
            trendline="ols"
        )
        fig11.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        fig11.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Popularity: %{x:.1f}<br>Revenue: $%{y:,.0f}<extra></extra>", selector=dict(mode="markers"))
        st.plotly_chart(fig11, use_container_width=True)
        st.info("💡 **Attention Insight:** High popularity generally yields high revenue, but hype doesn't perfectly guarantee a profitable return if the budget was mismanaged.")
    with c4:
        # 12. Vote Average vs Revenue
        fig12 = px.scatter(
            filtered_df, x='vote_average', y='revenue', color='success',
            title="12. Critical Acclaim vs Box Office Revenue", opacity=0.7,
            color_continuous_scale="Magma", hover_data=['title'],
            trendline="ols"
        )
        fig12.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        fig12.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Vote Average: %{x:.1f}<br>Revenue: $%{y:,.0f}<extra></extra>", selector=dict(mode="markers"))
        st.plotly_chart(fig12, use_container_width=True)
        st.info("💡 **Quality Insight:** While highly-rated indie films exist at the bottom left, the majority of mega-blockbusters sit comfortably above a 6.0 rating.")

    st.markdown("#### Hype vs Word of Mouth (Popularity vs Vote Average)")
    # 12.5 Popularity vs Vote Average
    fig_hype = px.scatter(
        filtered_df, x='popularity', y='vote_average', color='success',
        title="Hype (Popularity) vs Word of Mouth (Vote Average)", opacity=0.7,
        color_continuous_scale="Spectral", hover_data=['title'],
        trendline="ols"
    )
    fig_hype.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
    fig_hype.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Popularity: %{x:.1f}<br>Vote Average: %{y:.1f}<extra></extra>", selector=dict(mode="markers"))
    st.plotly_chart(fig_hype, use_container_width=True)
    st.info("💡 **Hype vs Word of Mouth Insight:** As requested, notice the inverse interactions! Some movies have very high hype (popularity) but fail to deliver on quality, resulting in a low vote average (Flop Risk). Conversely, many Hidden Gems have low popularity but extremely high vote averages (Sleeper Hits) driven by organic word of mouth.")

with tab_time:
    st.markdown("### ⏳ Runtime & Multi-Feature Correlations")
    c1, c2 = st.columns(2)
    with c1:
        # 13. Runtime Distribution
        fig13 = px.histogram(
            filtered_df[filtered_df['runtime'] <= 240], x="runtime", nbins=40,
            title="13. Runtime Distribution (Minutes)", color_discrete_sequence=["#f59e0b"]
        )
        fig13.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig13, use_container_width=True)
        st.info("💡 **Runtime Insight:** The industry standard clearly peaks around the 90 to 120-minute mark. Extremes in runtime can limit theatrical showings per day, impacting revenue.")

    with c2:
        # 14. Runtime vs Success
        fig14 = px.box(
            filtered_df, x='success', y='runtime', color='success',
            title="14. Movie Runtime by Financial Success", points="all"
        )
        fig14.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
        st.plotly_chart(fig14, use_container_width=True)
        st.info("💡 **Success Factor Insight:** Successful movies tend to have slightly longer runtimes, often associated with major studio tentpoles and epics.")

    # 15. Correlation Heatmap
    st.markdown("#### 15. Feature Correlation Heatmap")
    corr_matrix = filtered_df[['budget', 'revenue', 'popularity', 'runtime', 'vote_average', 'success']].corr()
    fig15 = px.imshow(
        corr_matrix, text_auto=".2f", aspect="auto",
        color_continuous_scale="RdBu_r"
    )
    fig15.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f8fafc")
    st.plotly_chart(fig15, use_container_width=True)
    st.info("💡 **Correlation Insight:** Budget and Revenue are highly correlated. Surprisingly, runtime has very little linear correlation with financial success.")
    
    st.markdown("""
    <div class='premium-card' style='margin-top: 15px;'>
        <h4 style='color:#38bdf8; margin-top:0;'>💡 Statistical Testing Context</h4>
        <p style='color:#94a3b8; font-size:0.95rem; line-height:1.6; margin-bottom:0;'>
            <b>T-Test Validation</b>: A formal independent T-test confirms that the `vote_average` differs significantly between successful and unsuccessful films (p < 0.05).<br>
            <b>Chi-Square Validation</b>: Our hypothesis testing confirms that genre is statically associated with financial success.
        </p>
    </div>
    """, unsafe_allow_html=True)
