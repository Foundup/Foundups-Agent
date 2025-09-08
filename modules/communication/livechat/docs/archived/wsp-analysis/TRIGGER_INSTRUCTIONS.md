
# Stream Trigger Instructions

## File Trigger (Currently Active)

To immediately wake up the bot and check for streams:

1. **Windows Command Prompt:**
   echo TRIGGER > stream_trigger.txt

2. **Windows PowerShell:**
   "TRIGGER" | Out-File stream_trigger.txt

3. **Touch the file (updates modification time):**
   copy /b stream_trigger.txt +,,

The bot will immediately check for streams when triggered.

## Future Triggers (Not Yet Implemented)

- API Endpoint: POST to /trigger
- Discord Webhook: Send message to bot
- Telegram Bot: Send /check command
