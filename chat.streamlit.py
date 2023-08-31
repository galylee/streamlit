import streamlit as st
import openai

# Set the OpenAI API key
openai.api_key = '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'

# Title
st.title("ChatGPT Chatbot")

# User input
user_input = st.text_input("You: ")

# GPT-3 Model
if user_input:
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=user_input,
        temperature=0.5,
        max_tokens=100
    )
    
    # Bot response
    st.write("Bot: ", response.choices[0].text.strip())
