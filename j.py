import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from textblob import TextBlob
import openai
import nltk
nltk.download('punkt')
nltk.download('wordnet')

def correct_spelling(input_text):
    if not input_text:
        return input_text

    blob = TextBlob(input_text)
    corrected_words = [word.correct() for word in blob.words]
    return " ".join(corrected_words)
def chat_with_gpt(input_topic):
    corrected_topic = correct_spelling(input_topic)

    # Make API call to ChatGPT
    api_key = 'use your api key'
    openai.api_key = api_key

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use GPT-3.5 engine
            prompt=corrected_topic,
            max_tokens=100
        )

        if response and 'choices' in response and len(response['choices']) > 0:
            answer = response['choices'][0]['text'].strip()
            return answer
    except Exception as e:
        st.error(f"Error in API call: {e}")

    return "Error in API call. Please try again later."

def save_chat_to_pdf(chat_list):
    doc = SimpleDocTemplate("chat_output.pdf", pagesize=letter)
    table_data = [["User", "Bot"]] + [[chat, chat_list[i+1]] for i, chat in enumerate(chat_list) if i % 2 == 0]
    table = Table(table_data)
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])
    table.setStyle(style)
    doc.build([table])
    st.success("Chat history saved as PDF.")

def main():
    st.set_page_config(layout="wide")

    # Initialize SessionState
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    st.title("Ask Your Chatbot")
    st.sidebar.title("Chat History")
    prev_chats = st.sidebar.text_area("Chat History", value="\n".join(st.session_state.chat_history), height=400)

    new_chat_button = st.sidebar.button("New Chat")

    if new_chat_button:
        prev_chats += "\n\n"

    input_topic = st.text_input("Enter your topic:")
    corrected_question = correct_spelling(input_topic)

    if corrected_question and corrected_question != input_topic:
        st.subheader("Did you mean this?")
        st.write(corrected_question)

    if st.button("Get Answer"):
        if input_topic:
            answer = chat_with_gpt(input_topic)
            prev_chats += f"\nUser: {input_topic}\nBot: {answer}\n"

            st.subheader("Answer :")
            st.write(answer)
        else:
            st.warning("Please enter a topic to get an answer.")

    st.sidebar.text("Close the sidebar to preserve chat history.")
    st.sidebar.text("You can reopen the sidebar to see previous chats.")
    st.sidebar.text("To start a new chat, click 'New Chat'.")

    # Store updated chat history in SessionState
    st.session_state.chat_history = prev_chats.split("\n")

    # Save chat history to PDF
    if st.button("Save Chat History as PDF"):
        save_chat_to_pdf(st.session_state.chat_history)

if __name__ == "__main__":
    main()
