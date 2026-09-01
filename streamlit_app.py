import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("Select Page")

page1 = st.Page('Lab1.py', title="Lab 1")
page2 = st.Page('Lab2.py', title="Lab 2", default=True)

pg = st.navigation([page1, page2])
st.set_page_config(page_title="Labs")
pg.run()