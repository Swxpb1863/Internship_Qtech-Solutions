import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
import librosa
import time  # Import time module for sleep function

# Load your trained XGBoost model
model = xgb.Booster()
model.load_model('model.pkl')  # Ensure you are using the correct model file type

def extract_features(file_name):
    try:
        audio_data, sample_rate = librosa.load(file_name, sr=None, res_type='kaiser_fast')

        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        mfccs_mean = np.mean(mfccs.T, axis=0)

        # Extract Chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
        chroma_mean = np.mean(chroma.T, axis=0)

        # Extract Mel Spectrogram
        mel = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
        mel_mean = np.mean(mel.T, axis=0)

        # Extract Tempo (Rhythm)
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sample_rate)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sample_rate)

        # Combine all features into a single array
        features = np.hstack([mfccs_mean, chroma_mean, mel_mean, tempo])
        return features
    
    except Exception as e:
        print(f"Error encountered while parsing file: {file_name}, Error: {e}")
        return None

# Define a list of genres
genres = ['Blues', 'Classical', 'Country', 'Disco', 'HipHop', 
          'Jazz', 'Metal', 'Pop', 'Reggae', 'Rock']


st.markdown(
    """
    <style>
    .big-font {
        font-size: 42px !important;
        text-align: center;
        font-weight: bold;
        
    }
    .medium-font {
        font-size: 20px !important;
    }
    .small-font {
        font-size: 20px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<p class='big-font'>Music Genre Classifier</p>", unsafe_allow_html=True)


st.markdown("<p class='small-font'>Upload your audio file:</p>", unsafe_allow_html=True)
# File uploader
uploaded_file = st.file_uploader("Preferred file extension: .wav", type='wav')

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open("temp.wav", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Add a music player to play the uploaded audio
    st.audio(uploaded_file, format='audio/wav')  # Display the audio player

    # Extract features
    features = extract_features("temp.wav")
    
    if features is not None:
        # Convert features to DataFrame
        features_df = pd.DataFrame([features])
        
        # Convert DataFrame to DMatrix for prediction
        dtest = xgb.DMatrix(features_df)
        
        # Create a placeholder for the prediction result
        prediction_placeholder = st.empty()
        prediction_placeholder.write("Analyzing the music...")  # Show analyzing message
        
        # Pause for 5 seconds
        time.sleep(5)
        
        # Make prediction
        prediction = model.predict(dtest)
        predicted_genre = genres[np.argmax(prediction)]  # Use argmax to get the genre index
        
        # Update the placeholder with the prediction result
        prediction_placeholder.write(f"<p class='medium-font'>The predicted genre is: <strong>{predicted_genre}</strong></p>", unsafe_allow_html=True)
    else:
        st.error("Feature extraction failed.")
