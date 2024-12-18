import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.utils import resample
import pickle
import re

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

# Preprocess reviews (Remove special characters and convert to lowercase)
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters and numbers
    text = text.lower()                      # Convert to lowercase
    return text

data["reviewText"] = data["reviewText"].fillna("").apply(preprocess_text)

# Downsampling 5.0 and 4.0 ratings (as before, if needed)
positive_reviews = data[data["sentiment"] == "Positive"]
five_star_reviews = positive_reviews[positive_reviews["overall"] == 5.0]
four_star_reviews = positive_reviews[positive_reviews["overall"] == 4.0]

five_star_reviews_downsampled = resample(five_star_reviews, replace=False, random_state=42)
four_star_reviews_downsampled = resample(four_star_reviews, replace=False, random_state=42)

other_reviews = data[~data["sentiment"].isin(["Positive"])]

balanced_data = pd.concat([five_star_reviews_downsampled, four_star_reviews_downsampled, other_reviews])

# Split the dataset
X = balanced_data["reviewText"]
y = balanced_data["sentiment"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Create a pipeline with TF-IDF and Naive Bayes
model_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10000, stop_words="english", ngram_range=(1, 2), min_df=2, max_df=0.75)),
    ("nb", MultinomialNB(alpha=0.03))  # You can experiment with alpha values (e.g., 1, 0.5)
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

print("Model has been trained and saved as naive_bayes_model.pkl")
