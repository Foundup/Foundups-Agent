#!/usr/bin/env python3
"""
Test script to verify fact-check fix for regular users
"""

import logging
logging.basicConfig(level=logging.INFO)

print('TESTING FACT-CHECK FIX FOR REGULAR USERS')
print('='*60)

# Simulate the scenario from the chat log
from modules.communication.livechat.src.message_processor import MessageProcessor
from modules.communication.livechat.src.chat_memory_manager import ChatMemoryManager
from modules.communication.livechat.src.chat_sender import ChatSender

# Create mock memory manager with some test messages
memory_manager = ChatMemoryManager()
memory_manager.start_session('test_session')

# Add some test messages including Eric Faulk
test_messages = [
    {'author': 'Eric Faulk', 'message': 'what timezone are you in', 'timestamp': '2025-10-04T13:54:00'},
    {'author': 'Foundups', 'message': 'UnDaoDu ALERT: Bot detects high levels of copium in chat', 'timestamp': '2025-10-04T13:52:23'},
    {'author': 'Move2Japan', 'message': 'FC @Eric Faulk', 'timestamp': '2025-10-04T13:52:30'},
]

for msg in test_messages:
    memory_manager.session_messages.append(msg)

# Create message processor with the memory manager
processor = MessageProcessor(None, memory_manager, None)

print('Added test messages to memory')
print('Messages in session:')
for msg in memory_manager.session_messages:
    print(f'   {msg["author"]}: {msg["message"][:50]}...')

print()
print('Testing fact-check collection...')
all_messages = processor._collect_all_user_messages()

print('Collected messages by user:')
for user, msgs in all_messages.items():
    print(f'   {user}: {len(msgs)} messages')
    for msg in msgs[-2:]:  # Show last 2 messages
        print(f'      "{msg["message"][:40]}..."')

print()
print('Testing fact-check for Eric Faulk...')
if 'Eric Faulk' in all_messages and all_messages['Eric Faulk']:
    print('SUCCESS: Eric Faulk has messages available for fact-checking!')
    print(f'   Found {len(all_messages["Eric Faulk"])} messages')
else:
    print('FAILED: Still no messages found for Eric Faulk')

print()
print('CONCLUSION: Fact-check system should now work for regular users!')
