import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("IST688 Lab")

page1 = st.Page('Lab1.py', title="Lab 1")
page2 = st.Page('Lab2.py', title="Lab 2")
page3 = st.Page('Lab3.py', title="Lab 3")
page4 = st.Page('Lab4.py', title="Lab 4")
page5 = st.Page('Lab5.py', title="Lab 5")
page6 = st.Page('LabLangChain.py', title="Lab 6", default=True)

pg = st.navigation([page1, page2, page3, page4, page5])
st.set_page_config(page_title="Labs")
pg.run()