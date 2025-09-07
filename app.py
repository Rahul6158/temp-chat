import streamlit as st
import random
import string
from datetime import datetime
import time

# Global dictionary to store chat rooms and messages (in production, use a proper data store)
if 'chat_rooms' not in st.session_state:
    st.session_state.chat_rooms = {}

def generate_room_code(length=6):
    """Generate a random room code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def initialize_session_state():
    """Initialize all necessary session state variables"""
    if 'room_code' not in st.session_state:
        st.session_state.room_code = None
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'last_update' not in st.session_state:
        st.session_state.last_update = 0

def create_or_join_room(room_code, username):
    """Create a new room or join an existing one"""
    if room_code not in st.session_state.chat_rooms:
        st.session_state.chat_rooms[room_code] = {
            'users': {username},
            'messages': [],
            'created_at': datetime.now().timestamp()
        }
    else:
        st.session_state.chat_rooms[room_code]['users'].add(username)
    
    st.session_state.room_code = room_code

def leave_room(room_code, username):
    """Remove user from room"""
    if room_code in st.session_state.chat_rooms:
        if username in st.session_state.chat_rooms[room_code]['users']:
            st.session_state.chat_rooms[room_code]['users'].remove(username)
            
        # Clean up empty rooms after a while
        if len(st.session_state.chat_rooms[room_code]['users']) == 0:
            # Keep messages for 5 minutes after last user leaves
            st.session_state.chat_rooms[room_code]['expires_at'] = datetime.now().timestamp() + 300

def send_message(room_code, username, message):
    """Add a message to the room"""
    if room_code in st.session_state.chat_rooms:
        timestamp = datetime.now().timestamp()
        st.session_state.chat_rooms[room_code]['messages'].append({
            'username': username,
            'message': message,
            'timestamp': timestamp
        })
        return True
    return False

def get_messages(room_code, since=0):
    """Retrieve messages from a room since a specific timestamp"""
    if room_code in st.session_state.chat_rooms:
        return [msg for msg in st.session_state.chat_rooms[room_code]['messages'] if msg['timestamp'] > since]
    return []

def get_users_in_room(room_code):
    """Get list of users in a room"""
    if room_code in st.session_state.chat_rooms:
        return list(st.session_state.chat_rooms[room_code]['users'])
    return []

def cleanup_expired_rooms():
    """Remove rooms that have been empty for too long"""
    current_time = datetime.now().timestamp()
    rooms_to_delete = []
    
    for room_code, room_data in st.session_state.chat_rooms.items():
        if 'expires_at' in room_data and room_data['expires_at'] < current_time:
            rooms_to_delete.append(room_code)
    
    for room_code in rooms_to_delete:
        del st.session_state.chat_rooms[room_code]

def main():
    st.title("💬 Real-Time Temporary Chat App")
    
    initialize_session_state()
    cleanup_expired_rooms()
    
    # Sidebar for room operations
    with st.sidebar:
        st.header("Chat Room")
        
        if st.session_state.room_code:
            room_users = get_users_in_room(st.session_state.room_code)
            st.success(f"Connected to room: {st.session_state.room_code}")
            st.write(f"Users in room: {', '.join(room_users) if room_users else 'Just you'}")
            
            if st.button("Leave Room"):
                leave_room(st.session_state.room_code, st.session_state.username)
                st.session_state.room_code = None
                st.rerun()
        else:
            # Username input
            st.session_state.username = st.text_input("Enter your username:", value=st.session_state.username, max_chars=20)
            
            # Create new room
            if st.button("Create New Room"):
                if st.session_state.username:
                    room_code = generate_room_code()
                    create_or_join_room(room_code, st.session_state.username)
                    st.rerun()
                else:
                    st.error("Please enter a username first")
            
            st.divider()
            
            # Join existing room
            room_to_join = st.text_input("Enter room code to join:", max_chars=6).upper()
            if st.button("Join Room"):
                if st.session_state.username:
                    if room_to_join and len(room_to_join) == 6:
                        create_or_join_room(room_to_join, st.session_state.username)
                        st.rerun()
                    else:
                        st.error("Please enter a valid 6-character room code")
                else:
                    st.error("Please enter a username first")
    
    # Main chat area
    if st.session_state.room_code:
        if not st.session_state.username:
            st.warning("Please set your username in the sidebar first!")
            return
            
        room_code = st.session_state.room_code
        st.header(f"Room: {room_code}")
        
        # Display chat messages
        chat_container = st.container()
        
        # Auto-refresh every 2 seconds to get new messages
        if time.time() - st.session_state.last_update > 2:
            st.session_state.last_update = time.time()
            st.rerun()
        
        with chat_container:
            messages = get_messages(room_code)
            for msg in messages:
                with st.chat_message(msg["username"]):
                    st.write(f"**{msg['username']}**: {msg['message']}")
                    st.caption(datetime.fromtimestamp(msg['timestamp']).strftime("%H:%M:%S"))
        
        # Chat input
        if prompt := st.chat_input("Type your message..."):
            if send_message(room_code, st.session_state.username, prompt):
                st.session_state.last_update = time.time()
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
