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
