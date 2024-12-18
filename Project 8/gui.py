import streamlit as st
import numpy as np
import librosa
import librosa.display
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
from io import BytesIO


# Load the trained model
@st.cache_resource
def load_ser_model():
    model = load_model("ser_model.keras")
    return model

# Function to extract MFCC features
def extract_mfcc(filename, n_mfcc=40):
    y, sr = librosa.load(filename, duration=3, offset=0.5)
    mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc).T, axis=0)
    return mfcc

# Function to plot waveform
def plot_waveform(audio_data, sampling_rate):
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(audio_data, sr=sampling_rate, alpha=0.8)
    plt.title("Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return buf

# Class labels
emotion_labels = ['anger', 'disgust', 'fear', 'happy', 'neutral', 'surprise', 'sad']

# Streamlit App
st.title("Speech Emotion Recognition")
st.write("Upload a `.wav` file to predict the emotion and view the audio waveform.")

# File uploader
uploaded_file = st.file_uploader("Choose a WAV file", type=["wav"])

if uploaded_file is not None:
    # Display audio player
    st.audio(uploaded_file, format="audio/wav")
    
    # Load the audio file for waveform and features
    y, sr = librosa.load(uploaded_file, duration=3, offset=0.5)
    
    # Visualize the audio waveform
    st.subheader("Waveform")
    waveform_plot = plot_waveform(y, sr)
    st.image(waveform_plot, caption="Audio Waveform", use_container_width=True)
    
    # Extract MFCC features
    mfcc_features = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
    mfcc_features = np.expand_dims(mfcc_features, axis=-1)  # Add channel dimension
    mfcc_features = np.expand_dims(mfcc_features, axis=0)  # Add batch dimension

    # Load model and make prediction
    model = load_ser_model()
    prediction = model.predict(mfcc_features)
    predicted_label = emotion_labels[np.argmax(prediction)]
    
    # Display the prediction
    st.write(f"### Predicted Emotion: *{predicted_label}*")
