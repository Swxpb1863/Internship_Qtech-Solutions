import streamlit as st
from transformers import pipeline

# Load the sentiment analysis model
@st.cache_resource
def load_model():
    return pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

# Streamlit App UI
st.title("Sentiment Analysis of Customer Reviews")
st.write("Enter a customer review below to analyze its sentiment (Positive, Negative, or Neutral).")

# Text area for input
review = st.text_area("Customer Review", placeholder="Type or paste the review here...")

# Label mapping for sentiment
label_mapping = {
    "LABEL_0": "Negative",
    "LABEL_1": "Neutral",
    "LABEL_2": "Positive"
}

# Load the model
sentiment_model = load_model()

# Analyze sentiment
if st.button("Analyze Sentiment"):
    if review.strip():
        result = sentiment_model(review)
        raw_label = result[0]['label']
        sentiment = label_mapping.get(raw_label, "Unknown")  # Map label to human-readable sentiment
        score = result[0]['score']

        # Display result
        st.write(f"### Sentiment: {sentiment}")
        st.write(f"### Confidence Score: {score:.2f}")
    else:
        st.error("Please enter a valid review.")
