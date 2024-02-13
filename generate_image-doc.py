# Import necessary libraries
import streamlit as st
import openai
import json
import requests
from datetime import datetime
import re

# Function to check if running on a PC


def isOnPC():
    onPC = False
    try:
        import platform
        platform = platform.processor()
        if "Intel64" in platform:
            onPC = True
    except:
        print("Running on cloud")
    return onPC

# Function to generate image using OpenAI API


def generate_image(OPENAI_API_KEY, query, n=1, size="1024x1024"):
    url = "https://api.openai.com/v1/images/generations"
    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + OPENAI_API_KEY}
    data = json.dumps({"prompt": query,
                       "n": n,
                       "size": size})
    response = requests.request("POST", url, headers=headers, data=data)
    image_url = json.loads(response.text)['data'][0]['url']
    return response, image_url

# Function to generate filename based on OpenAI ChatCompletion response


def generate_filename(OPENAI_API_KEY, query: str) -> str:
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant designed to summarize text to three words ONLY"},
            {"role": "user", "content": query}
        ],
    )
    generation_date = datetime.today().strftime("%Y%m%d")
    summary = response.choices[0].message.content
    summary = re.sub('[^ a-zA-Z]', "", summary)
    filename = "img/" + generation_date + \
        "_" + summary.replace(" ", "_") + ".jpg"
    return filename


# Streamlit UI setup
st.title("Image Generator")

with st.form("my_form"):
    # User input for OpenAI API key and query
    OPENAI_API_KEY = st.text_input("OPENAI_API_KEY")
    query = st.text_input("Query")

    print()

    # Submit button
    submitted = st.form_submit_button("Submit")
    if submitted:
        # Generate image using OpenAI API
        response, image_url = generate_image(
            OPENAI_API_KEY, query, n=1, size="1024x1024")

        # Display generated image URL as a clickable link
        text_string_variable = "Generated Image URL"
        link = f'[{text_string_variable}]({image_url})'
        st.markdown(link)

        # Generate filename and download image if running on PC
        filename = generate_filename(OPENAI_API_KEY, query)
        if response.status_code == 200:
            if isOnPC():
                img_data = requests.get(image_url).content
                with open(filename, "wb") as image:
                    image.write(img_data)

            st.text("Generated")
            st.image(image_url, caption=query)
