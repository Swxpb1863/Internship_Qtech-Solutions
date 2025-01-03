import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# Initialize the summarization pipeline using BART or T5 model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to scrape the article content from the URL
def fetch_article(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the article content (may vary depending on website structure)
        paragraphs = soup.find_all('p')
        article_text = " ".join([para.get_text() for para in paragraphs])

        # Return the article text
        return article_text
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("News Article Summarizer")
st.write("Enter a URL of a news article, and the system will generate a concise summary.")

# Input field for URL
url = st.text_input("Enter the URL of the news article:")

# Process the article and generate the summary
if url:
    st.write("Fetching article...")
    
    # Get article content
    article_content = fetch_article(url)
    
    if "Error" not in article_content:
        st.write("Article fetched successfully! Generating summary...")
        
        # Generate summary using BART
        summary = summarizer(article_content, max_length=300, min_length=50, do_sample=False)
        
        # Display the summary
        st.write("### Summary:")
        st.write(summary[0]['summary_text'])
    else:
        st.error("Failed to fetch article content. Please check the URL and try again.")
