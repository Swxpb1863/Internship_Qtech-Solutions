import streamlit as st
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load dataset and train the model
@st.cache_resource
def train_naive_bayes_model():
    # Load dataset
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

    # Split the dataset
    X = data["reviewText"].fillna("")  # Fill missing reviews with empty strings
    y = data["sentiment"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a pipeline with TF-IDF and Naive Bayes
    model_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000)),
        ("nb", MultinomialNB())
    ])

    # Train the model
    model_pipeline.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model_pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc:.2f}")

    # Save the trained model
    with open("naive_bayes_model.pkl", "wb") as file:
        pickle.dump(model_pipeline, file)

    return model_pipeline

# Load the pre-trained model
@st.cache_resource
def load_model():
    with open("naive_bayes_model.pkl", "rb") as file:
        return pickle.load(file)

# Streamlit App UI
st.title("Sentiment Analysis of Customer Reviews")
st.write("Enter a customer review below to analyze its sentiment (Positive, Negative, or Neutral).")

# Text area for input
review = st.text_area("Customer Review", placeholder="Type or paste the review here...")

# Load the Naive Bayes model
model = load_model()

# Analyze sentiment
if st.button("Analyze Sentiment"):
    if review.strip():
        # Predict sentiment
        prediction = model.predict([review])
        sentiment = prediction[0]

        # Display result
        st.write(f"### Sentiment: {sentiment}")
    else:
        st.error("Please enter a valid review.")
