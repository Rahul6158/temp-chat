import streamlit as st
import random
import string

def generate_room_code(length=6):
    """Generate a random room code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def initialize_session_state():
    """Initialize all necessary session state variables"""
    if 'room_code' not in st.session_state:
        st.session_state.room_code = None
    if 'messages' not in st.session_state:
        st.session_state.messages = {}
    if 'username' not in st.session_state:
        st.session_state.username = ""

def main():
    st.title("💬 Temporary Chat App")
    
    initialize_session_state()
    
    # Sidebar for room operations
    with st.sidebar:
        st.header("Chat Room")
        
        if st.session_state.room_code:
            st.success(f"Connected to room: {st.session_state.room_code}")
            if st.button("Leave Room"):
                st.session_state.room_code = None
                st.rerun()
        else:
            # Username input
            st.session_state.username = st.text_input("Enter your username:", value=st.session_state.username)
            
            # Create new room
            if st.button("Create New Room"):
                room_code = generate_room_code()
                st.session_state.room_code = room_code
                st.session_state.messages[room_code] = []
                st.rerun()
            
            st.divider()
            
            # Join existing room
            room_to_join = st.text_input("Enter room code to join:", max_chars=6).upper()
            if st.button("Join Room"):
                if room_to_join and len(room_to_join) == 6:
                    if room_to_join not in st.session_state.messages:
                        st.session_state.messages[room_to_join] = []
                    st.session_state.room_code = room_to_join
                    st.rerun()
                else:
                    st.error("Please enter a valid 6-character room code")
    
    # Main chat area
    if st.session_state.room_code:
        if not st.session_state.username:
            st.warning("Please set your username in the sidebar first!")
            return
            
        st.header(f"Room: {st.session_state.room_code}")
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages[st.session_state.room_code]:
                with st.chat_message(message["name"]):
                    st.write(message["message"])
        
        # Chat input
        if prompt := st.chat_input("Type your message..."):
            # Add message to history
            new_message = {"name": st.session_state.username, "message": prompt}
            st.session_state.messages[st.session_state.room_code].append(new_message)
            
            # Display the new message immediately
            with st.chat_message(st.session_state.username):
                st.write(prompt)
            
            # Rerun to update the chat display
            st.rerun()
    else:
        # Welcome message when not in a room
        st.info("👋 Welcome to the Temporary Chat App!")
        st.write("To get started:")
        st.write("1. Enter a username in the sidebar")
        st.write("2. Create a new room or join an existing one using a 6-character code")
        st.write("3. Start chatting with others in the same room!")
        
        st.divider()
        st.warning("⚠️ Note: This is a temporary chat. All messages will be lost when the app is restarted.")

if __name__ == "__main__":
    main()
