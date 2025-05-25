import json
import os
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_log_file(filepath: str):
    """
    Reads a chat history file containing raw YouTube message JSON,
    extracts essential fields (timestamp, user_id, message) for text messages,
    and overwrites the file with the cleaned data in JSON Lines format.

    Args:
        filepath: The path to the chat history file to clean.
    """
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return

    logger.info(f"Starting cleanup for: {filepath}")
    cleaned_lines = []
    lines_processed = 0
    lines_kept = 0
    lines_skipped = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            for line in infile:
                lines_processed += 1
                line = line.strip()
                if not line:
                    lines_skipped += 1
                    continue
                
                try:
                    message_data = json.loads(line)
                    snippet = message_data.get('snippet', {})
                    
                    # Filter for actual text messages
                    if snippet.get('type') == 'textMessageEvent':
                        author = message_data.get('authorDetails', {})
                        user_id = author.get('channelId')
                        timestamp = snippet.get('publishedAt')
                        message_text = snippet.get('displayMessage')

                        # Ensure essential fields are present
                        if user_id and timestamp and message_text is not None:
                            log_entry = {
                                "timestamp": timestamp,
                                "user_id": user_id,
                                "message": message_text,
                                "topic": None, 
                                "mood": None   
                            }
                            cleaned_lines.append(json.dumps(log_entry))
                            lines_kept += 1
                        else:
                            logger.debug(f"Skipping line {lines_processed}: Missing essential fields.")
                            lines_skipped += 1
                    else:
                        logger.debug(f"Skipping line {lines_processed}: Not a textMessageEvent (type: {snippet.get('type')}).")
                        lines_skipped += 1
                        
                except json.JSONDecodeError:
                    logger.warning(f"Skipping line {lines_processed}: Malformed JSON.")
                    lines_skipped += 1
                except Exception as e:
                    logger.warning(f"Skipping line {lines_processed} due to unexpected error: {e}")
                    lines_skipped += 1

        # Overwrite the original file with cleaned content
        with open(filepath, 'w', encoding='utf-8') as outfile:
            for cleaned_line in cleaned_lines:
                outfile.write(cleaned_line + '\n')
                
        logger.info(f"Cleanup complete for: {filepath}")
        logger.info(f"Processed: {lines_processed}, Kept: {lines_kept}, Skipped: {lines_skipped}")

    except Exception as e:
        logger.error(f"Failed to process file {filepath}: {e}", exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean raw YouTube chat log files to JSON Lines format.")
    parser.add_argument("filepath", help="Path to the chat log file to clean.")
    
    args = parser.parse_args()
    
    clean_log_file(args.filepath) 