import streamlit as st
from jamaibase import JamAI, protocol as p
import time
import os
from dotenv import load_dotenv

# Load environment variables (optional)
load_dotenv()

# Constants
PROJECT_ID = "cheetn"  # Replace with your project ID
PAT = "your_pat_token"          # Replace with your PAT
TABLE_TYPE = p.TableType.chat
OPENER = "Hello! How can I help you today?"

# Initialize JamAI
jamai = JamAI(project_id=PROJECT_ID, token=PAT)

def create_new_chat():
    timestamp = int(time.time())
    new_table_id = f"Chat_{timestamp}"
    try:
        jamai.table.duplicate_table(
            table_type=TABLE_TYPE,
            table_id_src="example_agent",  # Replace with your agent ID
            table_id_dst=new_table_id,
            include_data=True,
            create_as_child=True
        )
        return new_table_id
    except Exception as e:
        st.error(f"Error creating new chat: {str(e)}")
        return None

def main():
    st.title("Simple Chat Demo")

    # Initialize session state
    if "table_id" not in st.session_state:
        new_table_id = create_new_chat()
        st.session_state.table_id = new_table_id
        st.session_state.messages = [{"role": "assistant", "content": OPENER}]

    # Create New Chat button
    if st.button("New Chat"):
        new_table_id = create_new_chat()
        if new_table_id:
            st.session_state.table_id = new_table_id
            st.session_state.messages = [{"role": "assistant", "content": OPENER}]
            st.rerun()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Stream the response
            for chunk in jamai.table.add_table_rows(
                table_type=TABLE_TYPE,
                request=p.RowAddRequest(
                    table_id=st.session_state.table_id,
                    data=[{"User": prompt}],
                    stream=True
                )
            ):
                if isinstance(chunk, p.GenTableStreamChatCompletionChunk):
                    if chunk.output_column_name == 'AI':
                        full_response += chunk.choices[0].message.content
                        message_placeholder.write(full_response + "▌")
            
            message_placeholder.write(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()