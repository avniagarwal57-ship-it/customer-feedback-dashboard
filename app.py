"""
Customer Feedback Dashboard
----------------------------
Sentiment analysis (TextBlob) + interactive visualizations (Plotly) 
served through a Streamlit web app.

Run with:  streamlit run app.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from textblob import TextBlob
from datetime import datetime

# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Customer Feedback Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------------------------------
@st.cache_data
def load_data(file) -> pd.DataFrame:
    """Load CSV into a DataFrame and parse dates."""
    df = pd.read_csv(file)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def analyze_sentiment(text: str):
    """Return (polarity, subjectivity, label) for a piece of text using TextBlob."""
    if not isinstance(text, str) or text.strip() == "":
        return 0.0, 0.0, "Neutral"
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
    return polarity, subjectivity, label


@st.cache_data
def enrich_with_sentiment(df: pd.DataFrame, text_col: str) -> pd.DataFrame:
    """Apply sentiment analysis to every row and add polarity/subjectivity/label columns."""
    results = df[text_col].apply(analyze_sentiment)
    df = df.copy()
    df["polarity"] = results.apply(lambda x: x[0])
    df["subjectivity"] = results.apply(lambda x: x[1])
    df["sentiment"] = results.apply(lambda x: x[2])
    return df


SENTIMENT_COLORS = {
    "Positive": "#2ECC71",
    "Neutral": "#F1C40F",
    "Negative": "#E74C3C",
}

# --------------------------------------------------------------------------
# SIDEBAR - DATA SOURCE & FILTERS
# --------------------------------------------------------------------------
st.sidebar.title("⚙️ Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload your feedback CSV", type=["csv"], help="Needs at least a text column."
)

use_sample = st.sidebar.checkbox("Use sample dataset", value=uploaded_file is None)

if uploaded_file is not None and not use_sample:
    raw_df = load_data(uploaded_file)
else:
    raw_df = load_data("data/sample_feedback.csv")

# Let the user pick which column holds the feedback text
# (use pandas' string-dtype check so this works whether pandas reports
# text columns as "object" (older pandas) or "str" (newer pandas))
text_columns = [c for c in raw_df.columns if pd.api.types.is_string_dtype(raw_df[c])]
default_text_col = "feedback_text" if "feedback_text" in raw_df.columns else (text_columns[0] if text_columns else None)

text_col = st.sidebar.selectbox(
    "Feedback text column",
    options=text_columns,
    index=text_columns.index(default_text_col) if default_text_col in text_columns else 0,
)

# Run sentiment analysis
df = enrich_with_sentiment(raw_df, text_col)

# Sidebar filters
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

sentiment_options = st.sidebar.multiselect(
    "Sentiment",
    options=["Positive", "Neutral", "Negative"],
    default=["Positive", "Neutral", "Negative"],
)

if "product" in df.columns:
    product_options = st.sidebar.multiselect(
        "Product",
        options=sorted(df["product"].dropna().unique().tolist()),
        default=sorted(df["product"].dropna().unique().tolist()),
    )
else:
    product_options = None

if "rating" in df.columns:
    min_r, max_r = int(df["rating"].min()), int(df["rating"].max())
    rating_range = st.sidebar.slider("Rating range", min_r, max_r, (min_r, max_r))
else:
    rating_range = None

# Apply filters
filtered_df = df[df["sentiment"].isin(sentiment_options)]
if product_options is not None:
    filtered_df = filtered_df[filtered_df["product"].isin(product_options)]
if rating_range is not None:
    filtered_df = filtered_df[
        (filtered_df["rating"] >= rating_range[0]) & (filtered_df["rating"] <= rating_range[1])
    ]

# --------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------
st.title("📊 Customer Feedback Dashboard")
st.caption("Sentiment analysis powered by TextBlob · Visuals powered by Plotly")

# --------------------------------------------------------------------------
# KPI CARDS
# --------------------------------------------------------------------------
total = len(filtered_df)
pos_pct = (filtered_df["sentiment"] == "Positive").mean() * 100 if total else 0
neu_pct = (filtered_df["sentiment"] == "Neutral").mean() * 100 if total else 0
neg_pct = (filtered_df["sentiment"] == "Negative").mean() * 100 if total else 0
avg_polarity = filtered_df["polarity"].mean() if total else 0
avg_rating = filtered_df["rating"].mean() if "rating" in filtered_df.columns and total else None

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Feedback", total)
k2.metric("😊 Positive %", f"{pos_pct:.1f}%")
k3.metric("😐 Neutral %", f"{neu_pct:.1f}%")
k4.metric("😠 Negative %", f"{neg_pct:.1f}%")
if avg_rating is not None:
    k5.metric("⭐ Avg Rating", f"{avg_rating:.2f}")
else:
    k5.metric("Avg Polarity", f"{avg_polarity:.2f}")

st.markdown("---")

# --------------------------------------------------------------------------
# ROW 1: Sentiment distribution + Polarity histogram
# --------------------------------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Sentiment Distribution")
    sentiment_counts = filtered_df["sentiment"].value_counts().reindex(
        ["Positive", "Neutral", "Negative"]
    ).fillna(0)
    fig_pie = px.pie(
        names=sentiment_counts.index,
        values=sentiment_counts.values,
        color=sentiment_counts.index,
        color_discrete_map=SENTIMENT_COLORS,
        hole=0.45,
    )
    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("Polarity Score Distribution")
    fig_hist = px.histogram(
        filtered_df,
        x="polarity",
        nbins=20,
        color="sentiment",
        color_discrete_map=SENTIMENT_COLORS,
        labels={"polarity": "Polarity (-1 negative → +1 positive)"},
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# --------------------------------------------------------------------------
# ROW 2: Sentiment over time + Rating vs Sentiment
# --------------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    if "date" in filtered_df.columns and filtered_df["date"].notna().any():
        st.subheader("Sentiment Trend Over Time")
        trend = (
            filtered_df.dropna(subset=["date"])
            .groupby([pd.Grouper(key="date", freq="D"), "sentiment"])
            .size()
            .reset_index(name="count")
        )
        fig_trend = px.line(
            trend,
            x="date",
            y="count",
            color="sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            markers=True,
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No 'date' column found — trend chart skipped.")

with c4:
    if "rating" in filtered_df.columns:
        st.subheader("Rating vs Sentiment Polarity")
        fig_scatter = px.scatter(
            filtered_df,
            x="rating",
            y="polarity",
            color="sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            hover_data=[text_col],
            size="subjectivity",
            size_max=14,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No 'rating' column found — scatter chart skipped.")

# --------------------------------------------------------------------------
# ROW 3: Sentiment by product (if available)
# --------------------------------------------------------------------------
if "product" in filtered_df.columns:
    st.subheader("Sentiment Breakdown by Product")
    prod_sentiment = (
        filtered_df.groupby(["product", "sentiment"]).size().reset_index(name="count")
    )
    fig_bar = px.bar(
        prod_sentiment,
        x="product",
        y="count",
        color="sentiment",
        color_discrete_map=SENTIMENT_COLORS,
        barmode="stack",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# --------------------------------------------------------------------------
# TOP POSITIVE / NEGATIVE FEEDBACK
# --------------------------------------------------------------------------
c5, c6 = st.columns(2)

with c5:
    st.subheader("🌟 Top Positive Feedback")
    top_pos = filtered_df.sort_values("polarity", ascending=False).head(5)
    for _, row in top_pos.iterrows():
        st.success(f"**Polarity {row['polarity']:.2f}** — {row[text_col]}")

with c6:
    st.subheader("⚠️ Top Negative Feedback")
    top_neg = filtered_df.sort_values("polarity", ascending=True).head(5)
    for _, row in top_neg.iterrows():
        st.error(f"**Polarity {row['polarity']:.2f}** — {row[text_col]}")

st.markdown("---")

# --------------------------------------------------------------------------
# RAW DATA TABLE + DOWNLOAD
# --------------------------------------------------------------------------
st.subheader("📋 Detailed Feedback Table")
st.dataframe(
    filtered_df.sort_values("polarity", ascending=False) if total else filtered_df,
    use_container_width=True,
)

csv_export = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download analyzed data as CSV",
    data=csv_export,
    file_name="analyzed_feedback.csv",
    mime="text/csv",
)

st.caption(
    f"Dashboard generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
    f"{total} feedback records analyzed"
)
