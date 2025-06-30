#!/usr/bin/env python3

"""
Script to apply the necessary fixes to livechat.py
Follows WSP protocol for systematic fixes
"""

import re

def main():
    # Read the current file
    with open('modules/livechat/src/livechat.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Update the _handle_emoji_trigger method to use banter_engine.process_input correctly
    old_banter_call = r'response = self\.banter_engine\.get_random_banter\(theme="greeting"\)'
    new_banter_call = '''# Use banter engine to process the specific emoji sequence  
            state_info, response = self.banter_engine.process_input(message_text)
            logger.debug(f"Banter engine returned state: {state_info}, response: {response}")'''
    
    content = re.sub(old_banter_call, new_banter_call, content)
    
    # Fix 2: Add bot channel ID method (insert after _handle_emoji_trigger method)
    bot_channel_method = '''
    async def _get_bot_channel_id(self):
        """
        Get the channel ID of the bot to prevent responding to its own messages.
        
        Returns:
            str: The bot's channel ID, or None if unable to retrieve
        """
        try:
            request = self.youtube.channels().list(part='id', mine=True)
            response = request.execute()
            items = response.get('items', [])
            if items:
                bot_channel_id = items[0]['id']
                logger.info(f"Bot channel ID identified: {bot_channel_id}")
                return bot_channel_id
        except Exception as e:
            logger.warning(f"Could not get bot channel ID: {e}")
        return None
'''
    
    # Insert after the _handle_emoji_trigger method ends
    insert_point = content.find('            return False\n        except Exception as e:\n            logger.error(f"Error processing emoji trigger for {author_name}: {str(e)}")\n            return False\n\n    def _create_log_entry')
    if insert_point != -1:
        content = content[:insert_point] + '            return False\n        except Exception as e:\n            logger.error(f"Error processing emoji trigger for {author_name}: {str(e)}")\n            return False\n' + bot_channel_method + '\n    def _create_log_entry' + content[insert_point + len('            return False\n        except Exception as e:\n            logger.error(f"Error processing emoji trigger for {author_name}: {str(e)}")\n            return False\n\n    def _create_log_entry'):]
    
    # Fix 3: Add self-response prevention to _handle_emoji_trigger
    old_rate_check = 'logger.info(f"Emoji sequence detected in message from {author_name}: {message_text}")\n        \n        # Check rate limiting'
    new_rate_check = '''logger.info(f"Emoji sequence detected in message from {author_name}: {message_text}")
        
        # Check if this is a self-message (bot responding to its own emoji)
        if hasattr(self, 'bot_channel_id') and self.bot_channel_id and author_id == self.bot_channel_id:
            logger.debug(f"Ignoring self-message from bot {author_name}")
            return False
        
        # Check rate limiting'''
    
    content = content.replace(old_rate_check, new_rate_check)
    
    # Fix 4: Add bot channel ID initialization to start_listening
    old_init = '''# Initialize chat session
                if not await self._initialize_chat_session():
                    return
                
                # Send greeting message'''
    new_init = '''# Initialize chat session
                if not await self._initialize_chat_session():
                    return

                # Get bot channel ID for self-response prevention
                self.bot_channel_id = await self._get_bot_channel_id()
                
                # Send greeting message'''
    
    content = content.replace(old_init, new_init)
    
    # Write the updated content
    with open('modules/livechat/src/livechat.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied all livechat fixes successfully!")
    print("🔧 Fixed:")
    print("  - Banter engine process_input tuple handling")
    print("  - Added _get_bot_channel_id method") 
    print("  - Added self-response prevention")
    print("  - Added bot channel ID initialization")

if __name__ == "__main__":
    main() 