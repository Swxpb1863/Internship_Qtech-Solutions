import streamlit as st
from transformers import pipeline
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Naive Bayes Model Functions
@st.cache_resource
def train_naive_bayes_model():
    data = pd.read_csv("amazon_reviews.csv")  # Replace with the path to your dataset

    # Map ratings to sentiment
    def map_sentiment(rating):
        if rating >= 4.0:
            return "Positive"
        elif rating == 3.0:
            return "Neutral"
        else:
            return "Negative"

    data["sentiment"] = data["overall"].apply(map_sentiment)

    X = data["reviewText"].fillna("")
    y = data["sentiment"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000)),
        ("nb", MultinomialNB())
    ])

    model_pipeline.fit(X_train, y_train)
    y_pred = model_pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Naive Bayes Model Accuracy: {acc:.2f}")

    with open("naive_bayes_model.pkl", "wb") as file:
        pickle.dump(model_pipeline, file)

    return model_pipeline

@st.cache_resource
def load_naive_bayes_model():
    with open("naive_bayes_model.pkl", "rb") as file:
        return pickle.load(file)

# RoBERTa Model Functions
@st.cache_resource
def load_roberta_model():
    return pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

# App UI
st.set_page_config(page_title="Sentiment Analysis App", layout="wide")

# Sidebar for model selection
st.sidebar.title("Model Selector")
selected_model = st.sidebar.radio(
    "Choose a Sentiment Analysis Model:",
    ("Home", "Naive Bayes", "RoBERTa"),
)

# Home Page
if selected_model == "Home":
    st.title("Welcome to the Sentiment Analysis App!")
    st.write("Choose a model from the sidebar to analyze customer reviews.")
    st.image("image.jpg")  # Replace with a relevant image URL if available

# Naive Bayes Model Page
elif selected_model == "Naive Bayes":
    st.title("Naive Bayes Sentiment Analysis")
    st.write("Enter a customer review below to analyze its sentiment (Positive, Negative, or Neutral).")

    review = st.text_area("Customer Review", placeholder="Type or paste the review here...")

    model = load_naive_bayes_model()

    if st.button("Analyze Sentiment (Naive Bayes)"):
        if review.strip():
            prediction = model.predict([review])
            sentiment = prediction[0]
            st.write(f"### Sentiment: {sentiment}")
        else:
            st.error("Please enter a valid review.")

# RoBERTa Model Page
elif selected_model == "RoBERTa":
    st.title("RoBERTa Sentiment Analysis")
    st.write("Enter a customer review below to analyze its sentiment (Positive, Negative, or Neutral).")

    review = st.text_area("Customer Review", placeholder="Type or paste the review here...")

    label_mapping = {
        "LABEL_0": "Negative",
        "LABEL_1": "Neutral",
        "LABEL_2": "Positive"
    }

    sentiment_model = load_roberta_model()

    if st.button("Analyze Sentiment (RoBERTa)"):
        if review.strip():
            result = sentiment_model(review)
            raw_label = result[0]['label']
            sentiment = label_mapping.get(raw_label, "Unknown")
            score = result[0]['score']
            st.write(f"### Sentiment: {sentiment}")
            st.write(f"### Confidence Score: {score:.2f}")
        else:
            st.error("Please enter a valid review.")
