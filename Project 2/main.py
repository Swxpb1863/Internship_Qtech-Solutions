import streamlit as st
import pandas as pd
from transformers import DistilBertTokenizer, DistilBertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained DistilBERT model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertModel.from_pretrained('distilbert-base-uncased')

# Load FAQ dataset
faq_data = pd.read_csv('faq_data.csv')

# Function to embed a sentence using DistilBERT
def embed_question(question):
    inputs = tokenizer(question, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding

# Precompute the embeddings of FAQ questions
faq_data['embedding'] = faq_data['question'].apply(lambda x: embed_question(x) if pd.notnull(x) else None)

# Function to find the most similar FAQ answer based on user input
def get_best_answer(user_input):
    user_embedding = embed_question(user_input)
    
    valid_faq_data = faq_data.dropna(subset=['embedding'])
    embeddings = list(valid_faq_data['embedding'])
    
    similarities = cosine_similarity([user_embedding], embeddings)
    best_match_idx = similarities.argmax()

    # Define a threshold for similarity. If the similarity is too low, return a fallback message.
    threshold = 0.6  # Adjust this value as needed
    if similarities[0][best_match_idx] < threshold:
        return "I do not have access to such information. Please contact customer service, which is available 24x7!"
    
    return valid_faq_data.iloc[best_match_idx]['answer']

# Initialize chat history in session state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'first_query_done' not in st.session_state:
    st.session_state['first_query_done'] = True

if 'clear_chat' not in st.session_state:
    st.session_state['clear_chat'] = False

# Function to clear the chat
def clear_chat():
    st.session_state['clear_chat'] = True

# Chatbot function
def chatbot():
    if st.session_state['clear_chat']:
        st.session_state['chat_history'] = []
        st.session_state['first_query_done'] = False
        st.session_state['user_input'] = ""
        st.session_state['clear_chat'] = False

    st.title("Chat with Me - Shoppify FAQs")
    col1, col2 = st.columns([5,1])
    with col1: 
        st.write("Have queries? Just ask, and I'll try to help you!")
    with col2:
        if st.session_state['first_query_done']:
            st.button("Clear Chat", on_click=clear_chat)
    user_input = st.text_input("You:", key='user_input')
    # Process user input and generate bot response
    if user_input:
        # Mark that the first query has been made
        st.session_state['first_query_done'] = True

        # Get the best answer from FAQ
        answer = get_best_answer(user_input)

        # Append the conversation to the chat history
        st.session_state['chat_history'].append({"user_message": user_input, "bot_message": answer})

    # Display the conversation history
    for chat in st.session_state['chat_history']:
        # For User message with icon on the right
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-end; align-items: center; margin-bottom: 10px;'>
                <div style="background-color: #daf0ff; padding: 10px; border-radius: 10px; text-align: right; max-width: 70%;">
                    <b>{chat['user_message']}</b>
                </div>
                <div style="margin-left: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/1946/1946429.png" alt="User" style="width: 30px; height: 30px; border-radius: 50%;">
                </div>
            </div>
        """, unsafe_allow_html=True)

        # For Bot message with icon on the left
        st.markdown(f"""
            <div style='display: flex; justify-content: flex-start; align-items: center; margin-bottom: 10px;'>
                <div style="margin-right: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png" alt="Bot" style="width: 30px; height: 30px; border-radius: 50%;">
                </div>
                <div style='background-color: #e1ffc7; padding: 10px; border-radius: 5px; max-width: 70%;'>
                    <b>{chat['bot_message']}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Run the chatbot
chatbot()
