import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="News Headline–Content Similarity", layout="wide")

st.title("📰 Headline vs Content Similarity Dashboard")

uploaded = st.file_uploader("Upload your CSV (with title, content, similarity)", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)
    st.success(f"Loaded {len(df)} articles ✅")

    # Show summary stats
    st.subheader("📊 Similarity Summary")
    st.write(df["similarity"].describe())

    # Plot distribution
    fig, ax = plt.subplots()
    ax.hist(df["similarity"], bins=30, color="skyblue", edgecolor="black")
    ax.set_title("Headline–Content Similarity Distribution")
    ax.set_xlabel("Similarity (0–1)")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    # Flag clickbait
    threshold = st.slider("Clickbait threshold", 0.0, 1.0, 0.45, step=0.01)
    low_sim = df[df["similarity"] < threshold].sort_values("similarity").head(20)

    st.subheader("🚨 Possible Clickbait Headlines")
    st.dataframe(low_sim[["title", "similarity"]])

    # Download results
    csv_out = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download processed CSV", csv_out, "results.csv", "text/csv")
else:
    st.info("Upload a CSV to get started.")
