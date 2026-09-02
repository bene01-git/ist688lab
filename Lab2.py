import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# Show title and description.
st.title("Lab 2")

summary_option = st.sidebar.selectbox(
    'Choose a summary format',
    ("100 words", "2 connecting paragraphs", "5 bullet points")
)

if st.sidebar.checkbox("Use advanced model"):
    selected_model = "gpt-5.4-mini" 
else:
    selected_model = "gpt-5.4-nano"

def read_pdf(pdf_file):
    pdf = PdfReader(pdf_file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"
    return text

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.secrets.OPENAI_API_KEY
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .pdf)", type=("txt", "pdf")
    )

    if uploaded_file:
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension == 'txt':
            document = uploaded_file.read().decode()
        elif file_extension == 'pdf':
            document = read_pdf(uploaded_file)
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n Summarize the document in {summary_option}",
            }
        ]

        st.write(f"Generating summary using: **{selected_model}**...")

        stream = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            stream=True,
        )
        st.write_stream(stream)
        st.write(stream)
