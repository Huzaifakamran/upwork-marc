import streamlit as st
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv
import fitz 
import os
load_dotenv()

# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

messages = []

# Function to extract text from different document types
def extract_text(uploaded_file, user_text):
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            text = uploaded_file.read()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            docx_file = Document(uploaded_file)
            text = "\n".join([paragraph.text for paragraph in docx_file.paragraphs])
        elif uploaded_file.type == "application/pdf":
            pdf_document = fitz.open(uploaded_file)
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text()
        else:
            st.warning("Please upload a valid text document (e.g., .txt)")
            return None
    elif user_text:
        text = user_text
    else:
        st.warning("Please upload a document or enter text in the text area.")
        return None

    return text

# Function to process user input and generate an answer
def generate_answer(question):

    user_dict = {"role": "user", "content": question}
    messages.append(user_dict)

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages
    )
    answer = completion.choices[0].message.content
    sys_dict = {"role": "system", "content": answer}
    messages.append(sys_dict)
    return answer

# Main Streamlit app
def main():
    try:
        st.title("Document Text Extractor and Q&A")

        # Sidebar for document upload
        st.sidebar.header("Upload Document")
        document = st.sidebar.file_uploader("Choose a document", type=["txt", "docx", "pdf"])

        # Text area for pasting text
        st.sidebar.header("Or Paste Text")
        user_text = st.sidebar.text_area("Paste your text here:")

        # Submit button for pasted text
        submit_button = st.sidebar.button("Submit")

        # Initialize session state
        if 'qa_history' not in st.session_state:
            st.session_state.qa_history = []

        # Main content area
        st.subheader("Document Text Extraction")

        # Extract text from the document or user-pasted text
        text = extract_text(document, user_text)

        if text is not None:
            sys_dict = {"role": "system", "content": text}
            messages.append(sys_dict)

            st.text_area("Document Text", text, height=300)

            # Q&A Section
            st.subheader("Ask a Question")

            # Input field for user question
            user_question = st.text_input("Type your question here:")
            if st.button("Get Answer"):
                if user_question:
                    # Generate answer and display
                    answer = generate_answer(user_question)
                    st.write("Answer:", answer)

                    # Store question and answer in history
                    st.session_state.setdefault('qa_history', []).append({
                        'question': user_question,
                        'answer': answer
                    })

            # Display Q&A history
            st.subheader("Q&A History")
            for item in st.session_state.qa_history:
                st.write(f"Question: {item['question']}")
                st.write(f"Answer: {item['answer']}")
                st.markdown("---")

    except Exception as e:
        st.write(e)

# Run the app
if __name__ == "__main__":
    main()