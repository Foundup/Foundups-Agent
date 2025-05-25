    def _check_trigger_patterns(self, message_text):
        """
        Check if a message contains any trigger patterns.
        
        Args:
            message_text (str): The message text to check
            
        Returns:
            bool: True if a trigger pattern was found, False otherwise
        """
        # Define trigger sequence by joining the trigger emojis
        trigger_sequence = ''.join(self.trigger_emojis)
        
        # Check for the emoji sequence in the message
        if trigger_sequence in message_text:
            return True
        return False 