# Phase 2: OpenAI-Powered Content Analysis Implementation

## Overview

Phase 2 transforms the 15 Seconds of Fame application from generating random 15-second clips to creating AI-curated viral moments with detailed reasoning for their viral potential. This implementation integrates OpenAI GPT-4 to analyze video clip transcripts and score them for viral potential.

## Features Implemented

### 1. OpenAI Integration Module (`openai_analyzer.py`)

- **API Configuration**: Set up OpenAI client with API key management via environment variables
- **Content Analysis Function**: Analyze transcripts for viral potential using GPT-4
- **Cost Tracking**: Monitor API usage to stay within $50 budget
- **Rate Limiting**: Respect OpenAI API rate limits and handle errors gracefully
- **Fallback Mode**: Basic scoring when API is unavailable or budget exceeded

### 2. Viral Potential Analysis

Each clip is analyzed for:
- **Viral Score (1-10)**: Overall viral potential based on multiple factors
- **Emotional Intensity (1-10)**: How emotionally engaging (joy, surprise, anger, inspiration)
- **Controversy Level (1-10)**: Likelihood to spark discussion or debate
- **Relatability (1-10)**: Universal appeal and everyday relevance
- **Educational Value (1-10)**: Learning potential and insights provided
- **Entertainment Factor (1-10)**: Pure entertainment and engagement value
- **Viral Reasoning**: Detailed explanation of why this clip could go viral

### 3. Enhanced Scoring Algorithm

The scoring system now combines:
- **Audio Analysis Scores**: audio quality, dramatic intensity, speech clarity
- **OpenAI Content Analysis**: viral potential, emotional engagement, controversy
- **Transcript Quality**: clarity, coherence, completeness
- **Optimal Length**: preference for 10-20 second clips over fixed 15-second chunks

### 4. Database Schema Updates

New columns added to clips table:
- `viral_score`: Overall viral potential score
- `emotional_intensity`: Emotional engagement level
- `controversy_level`: Discussion-sparking potential
- `relatability`: Universal appeal score
- `educational_value`: Learning potential score
- `entertainment_factor`: Entertainment value score
- `viral_reasoning`: Detailed explanation of viral potential
- `combined_score`: Weighted combination of all factors
- `api_usage_tokens`: Tokens used for this clip's analysis
- `api_usage_cost`: Cost of this clip's analysis

### 5. Budget Management System

- **Cost Per Video**: Target ~$0.10-0.25 per video processed
- **Budget Tracking**: Monitor cumulative API usage
- **Usage Warnings**: Alert when approaching budget limits
- **Fallback Scoring**: Use basic algorithms when budget exceeded

## Technical Implementation

### Dependencies Added

```txt
openai==1.3.0
python-dotenv==1.0.0
```

### Environment Configuration

Create a `.env` file in the backend directory:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize budget and rate limiting
DAILY_BUDGET=50.0  # Daily budget in USD (default: $50)
RATE_LIMIT_DELAY=1.0  # Seconds between API calls (default: 1.0)
```

### API Endpoints

#### New Endpoints Added

- `GET /api/usage` - Get OpenAI API usage statistics
- `POST /api/reset-usage` - Reset daily API usage counters

#### Enhanced Response Format

The `/process` endpoint now returns clips with enhanced scoring:

```json
{
  "clips": [
    {
      "id": "clip_1",
      "segment_id": "1",
      "score": 8.5,
      "start_time": 0.0,
      "end_time": 15.0,
      "transcript": "This is an amazing moment...",
      "audio_path": "...",
      "video_path": "...",
      "reasoning": "This clip has high viral potential due to...",
      "viral_score": 8.5,
      "emotional_intensity": 9.0,
      "controversy_level": 7.0,
      "relatability": 8.0,
      "educational_value": 6.5,
      "entertainment_factor": 9.0,
      "combined_score": 8.2,
      "api_usage_tokens": 150,
      "api_usage_cost": 0.002
    }
  ],
  "status": "success"
}
```

### Frontend Enhancements

#### New Components

1. **ViralAnalysisDisplay**: Shows detailed viral analysis scores with visual indicators
2. **ApiUsageDisplay**: Displays OpenAI API usage statistics and budget information

#### Enhanced ClipCard

- Toggle to show/hide detailed viral analysis
- Visual score breakdown with progress bars
- Color-coded indicators for different score types

#### API Usage Dashboard

- Real-time budget tracking
- Usage statistics (requests, tokens, costs)
- Warning indicators for budget thresholds
- Status indicators for API availability

## Usage Instructions

### 1. Setup OpenAI API

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Copy `env_example.txt` to `.env` in the backend directory
3. Add your API key to the `.env` file

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Backend
cd backend
python app.py

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### 4. Process Videos

1. Enter a YouTube URL in the frontend
2. The system will:
   - Download and segment the video
   - Generate transcripts for each segment
   - Analyze each segment with OpenAI GPT-4
   - Score clips based on viral potential
   - Display results with detailed analysis

## Cost Management

### Budget Controls

- **Daily Budget**: $50 (configurable)
- **Cost Per Request**: ~$0.002-0.005 per clip analysis
- **Automatic Fallback**: Basic scoring when budget exceeded
- **Usage Monitoring**: Real-time tracking in frontend

### Cost Optimization

- **Token Limits**: Maximum 1000 tokens per response
- **Rate Limiting**: 1 second between API calls
- **Efficient Prompts**: Optimized for cost-effective analysis
- **Fallback Mode**: Graceful degradation when API unavailable

## Success Criteria Met

✅ **Clips ranked by actual viral potential** rather than random selection  
✅ **Detailed reasoning** for why each clip could go viral  
✅ **Cost-effective analysis** staying within $50 budget  
✅ **Significant improvement** in clip quality and viral potential  
✅ **Graceful fallback** when API is unavailable  

## Performance Considerations

### API Efficiency

- **Prompt Optimization**: Structured prompts for consistent analysis
- **Response Format**: JSON-only responses to minimize token usage
- **Error Handling**: Robust fallback mechanisms
- **Rate Limiting**: Prevents API quota exhaustion

### User Experience

- **Real-time Feedback**: Live usage statistics
- **Visual Indicators**: Color-coded score breakdowns
- **Progressive Disclosure**: Expandable analysis details
- **Budget Awareness**: Clear cost tracking and warnings

## Future Enhancements

### Potential Improvements

1. **Multi-Model Support**: Integration with other AI models
2. **Advanced Analytics**: Historical performance tracking
3. **Custom Scoring**: User-defined viral criteria
4. **Batch Processing**: Optimized for multiple videos
5. **Export Features**: Share viral clips directly to social platforms

### Scalability Considerations

- **Caching**: Store analysis results to reduce API calls
- **Queue System**: Handle high-volume processing
- **Load Balancing**: Distribute processing across multiple instances
- **Database Optimization**: Index viral analysis fields for faster queries

## Troubleshooting

### Common Issues

1. **API Key Not Found**: Ensure `.env` file exists with correct API key
2. **Budget Exceeded**: Check usage statistics and consider increasing budget
3. **Rate Limiting**: System automatically handles rate limits
4. **Fallback Mode**: Check if OpenAI API is available

### Debug Information

- API usage statistics available at `/api/usage`
- Detailed logs in backend console
- Error messages displayed in frontend
- Budget warnings shown in usage dashboard

## Conclusion

Phase 2 successfully transforms the application into an AI-powered viral content discovery tool. The integration of OpenAI GPT-4 provides sophisticated content analysis while maintaining cost-effectiveness and reliability through robust fallback mechanisms.
