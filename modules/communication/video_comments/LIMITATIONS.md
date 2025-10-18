# YouTube API Limitations

## Community Posts - NOT SUPPORTED
As of 2025, YouTube Data API v3 does **NOT** support Community posts:
- Cannot read Community posts via API
- Cannot create Community posts via API  
- Cannot reply to Community posts via API

The Community tab at https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw is not accessible via official API.

## What IS Supported

### Video Comments [OK]
- **Read comments**: `commentThreads.list`
- **Post replies**: `comments.insert`
- **Delete comments**: `comments.delete`
- **Get comment threads**: Full conversation threads

### Limitations on Comments
- Cannot like/heart individual comments (only videos)
- 500 character limit per comment
- Rate limits apply (~50 requests/minute safe)
- No webhooks - must poll for new comments

## Our Solution

Since Community posts aren't available, we focus on:

1. **Video Comments** - Real-time dialogue on videos
2. **Live Chat** - During streams (already implemented)
3. **Polling Strategy** - Check every 5-15 seconds for real-time feel

## Move2Japan Channel
- Channel ID: `UC-LSSlOZwpGIRIYihaz8zCw`
- We monitor video comments on their uploads
- We engage in real-time dialogue when people comment
- Cannot access their Community tab programmatically

## Future Possibilities
If YouTube adds Community API support, we can enhance to include:
- Community post monitoring
- Community post responses
- Polls and engagement

For now, video comments provide the best autonomous engagement option.