import streamlit as st

st.set_page_config(page_title="About Application", page_icon="ℹ️", layout="wide")
st.title("About This Application ℹ️")
st.markdown("""
This application primarily serves as a dashboard for visualizing voice of the customers of certain jewellery stores in the UAE & US regions.\n
The review data we work on is extracted from the internet with the help of Google Maps Reviews Scraper created by Compass and maintained by Apify.\n
The data is processed and anlyzed by leveraging the power of OpenAI's GPT-5 model.
The application is built using Streamlit, a popular framework for creating interactive web applications in Python.
""")