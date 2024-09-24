import streamlit as st
import gdown
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import random

# Function to download file from Google Drive
def download_file_from_google_drive(file_id, output_file):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_file, quiet=False)

# Download and load the model
model_file_id = "1-2_TX-rMJYxhvAFRMYuGG38uvVksUd-7"  # Replace with your Google Drive file ID
model_file = "best_simple_LSTM.keras"

if not os.path.exists(model_file):
    with st.spinner('Downloading the model from Google Drive...'):
        download_file_from_google_drive(model_file_id, model_file)

model = load_model(model_file)

# Download Shakespeare text file
shakespeare_file_id = "1DIMeFhb40tE03Lay2gOXN40ytz1f3ptP"  # Replace with your Google Drive file ID
shakespeare_file = "shakespeare.txt"

if not os.path.exists(shakespeare_file):
    with st.spinner('Downloading Shakespeare text from Google Drive...'):
        download_file_from_google_drive(shakespeare_file_id, shakespeare_file)

# Load character mappings
# Read and process the text
with open(shakespeare_file, 'r', encoding='utf-8') as file:
    text = file.read()

# Only use the first 97,000 characters
text = text[1:97000]  # Cutting down to 97,000 characters

# Clean the text to remove unwanted characters like 'æ'
unwanted_chars = 'æ'  # You can add more characters to this string if needed
text = ''.join([char for char in text if char not in unwanted_chars])

characters = sorted(set(text))
char_to_index = {c: i for i, c in enumerate(characters)}
index_to_char = {i: c for i, c in enumerate(characters)}

SEQ_LENGTH = 40  # This should match your model's input sequence length

# Define the sample function
def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

# Define the generate_text function
def generate_text(seed_text, length, temperature):
    generated = seed_text
    sentence = seed_text[-SEQ_LENGTH:]
    
    for i in range(length):
        x_predictions = np.zeros((1, SEQ_LENGTH, len(characters)))
        for t, char in enumerate(sentence):
            if char in char_to_index:
                x_predictions[0, t, char_to_index[char]] = 1

        predictions = model.predict(x_predictions, verbose=0)[0]
        next_index = sample(predictions, temperature)
        next_character = index_to_char[next_index]

        generated += next_character
        sentence = sentence[1:] + next_character  # Shift the sentence window
    
    return generated

# Streamlit UI
st.title('ShakeGen: Simple LSTM Edition')

st.info('AI-powered Shakespearean Sonnet Generator using Simple LSTM')

# Sidebar content
st.sidebar.header("Model and Generation Information")

# Show model details
st.sidebar.subheader("Model Details")
st.sidebar.write(f"Sequence length: {SEQ_LENGTH}")
st.sidebar.write(f"Vocabulary size: {len(characters)}")

# Show the list of unique characters (vocabulary)
st.sidebar.subheader("Vocabulary List")
vocab_string = ', '.join(characters)
st.sidebar.write(f"Vocabulary: {vocab_string}")

# Textbox for user input seed
seed_text = st.text_input('Enter seed text for generation (optional)', '')

# Temperature slider
temperature = st.sidebar.slider('Select Temperature', 0.1, 2.0, value=0.5)

# Generate button
if st.sidebar.button('Generate'):
    if len(seed_text) < SEQ_LENGTH:
        st.warning(f"Please provide at least {SEQ_LENGTH} characters for the seed text.")
    else:
        generated_text = generate_text(seed_text, 600, temperature)  # Generate 600 characters of text
        if generated_text:
            st.markdown(f"**Generated Text:**\n\n{generated_text}")
