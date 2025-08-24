# 15 Seconds of Fame 🚀

**AI-Powered Viral Content Discovery**

A web application that analyzes YouTube videos to find the most viral 15-second clips using AI-powered analysis and machine learning. Perfect for content creators, marketers, and anyone looking to repurpose long-form content into engaging short clips.

## 🎯 Overview

15 Seconds of Fame automatically processes YouTube videos to identify the most engaging and shareable 15-second segments. The application uses advanced AI analysis to score video segments based on viral potential, helping content creators optimize their content for maximum engagement.

## ✨ Features

### 🎯 Core Functionality
- **Smart Video Segmentation**: Automatically splits videos into optimal 15-second clips
- **AI-Powered Analysis**: Uses OpenAI's GPT-4 models to analyze content virality
- **Viral Scoring**: Multi-dimensional scoring system (emotional intensity, controversy, relatability)
- **Audio Analysis**: Advanced audio processing for better clip selection
- **Real-time Processing**: Fast video processing with progress tracking

### 📚 Clip Library
- **Save Favorite Clips**: Build a personal library of your best viral clips
- **Search & Organize**: Find clips by transcript or viral reasoning
- **Easy Access**: Quick playback and management of saved clips

## 🏗️ Architecture

This is a production-ready application designed for reliability and performance:

- **Frontend**: React + TypeScript + Vite with Tailwind CSS
- **Backend**: FastAPI + Python with serverless deployment
- **AI Analysis**: OpenAI GPT-4 integration with cost optimization
- **Database**: SQLite with viral analysis schema
- **Deployment**: Vercel for frontend, Railway for backend

## 🚀 Quick Start

### Prerequisites

- Node.js (v18+)
- Python 3.9+
- OpenAI API key

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd 15-seconds-of-fame
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp env_example.txt .env
   # Edit .env with your OpenAI API key
   python app.py
   ```
   The backend API will be available at `http://localhost:8000`

## 📁 Project Structure

```
15-seconds-of-fame/
├── frontend/                           # React + Vite frontend
│   ├── src/
│   │   ├── components/                # React components
│   │   │   ├── VideoProcessor.tsx     # Main video processing interface
│   │   │   ├── ClipLibrary.tsx        # Saved clips library
│   │   │   ├── ClipCard.tsx           # Individual clip display
│   │   │   └── ...                    # Other components
│   │   ├── hooks/                     # Custom React hooks
│   │   ├── services/                  # API services
│   │   ├── types/                     # TypeScript types
│   │   └── utils/                     # Utility functions
│   ├── dist/                          # Build output
│   └── package.json                   # Frontend dependencies
├── backend/                           # FastAPI + Python backend
│   ├── app.py                        # Main FastAPI application
│   ├── viral_analyzer.py             # Viral analysis logic
│   ├── openai_analyzer.py            # OpenAI GPT-4 integration
│   ├── clipper.py                    # Video processing
│   ├── audio_analyzer.py             # Audio analysis
│   ├── scorer.py                     # Scoring algorithms
│   ├── database.py                   # Database operations
│   └── requirements.txt              # Python dependencies
├── vercel.json                       # Vercel deployment config
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

## 🚀 Deployment

This project is configured for production deployment:

- **Frontend**: Deployed on Vercel with automatic builds and CDN
- **Backend**: Deployed on Railway with serverless scaling
- **Database**: SQLite with automatic backups
- **AI Integration**: OpenAI GPT-4 with cost optimization

### Production Features

- **Auto-scaling**: Handles traffic spikes automatically
- **CDN**: Global content delivery for fast loading
- **Monitoring**: Real-time error tracking and performance metrics
- **Backup**: Automated database backups and recovery
- **SSL**: Secure HTTPS connections throughout

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
DAILY_BUDGET=50.0
RATE_LIMIT_DELAY=1.0
```

### API Endpoints

- `POST /process` - Process a YouTube video
- `GET /audio/{clip_id}` - Get audio file for a clip
- `GET /videos/{video_id}` - Get video information
- `POST /cleanup` - Clean up old files

## 📚 Documentation

- [Backend Documentation](./backend/README.md) - Detailed backend setup and API docs
- [Frontend Documentation](./frontend/README.md) - Frontend development guide
- [Phase 2 Implementation](./PHASE2_IMPLEMENTATION_SUMMARY.md) - AI integration and viral analysis

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Frontend linting
cd frontend
npm run lint

# Backend formatting
cd backend
black .
flake8 .
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 How It Works

### 1. Video Processing
- Input a YouTube URL
- Download and analyze the video
- Extract audio and generate transcripts
- Segment into 15-second clips

### 2. AI Analysis
- GPT-4 analyzes each clip for viral potential
- Scores based on emotional intensity, controversy, relatability
- Provides detailed reasoning for viral potential
- Ranks clips by engagement likelihood

### 3. Results
- View top viral clips with scores
- Play audio previews
- Save favorite clips to library
- Access detailed viral analysis

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4 API
- FastAPI for the excellent web framework
- React and Vite for the modern frontend experience
- Vercel and Railway for seamless deployment

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Built with ❤️ for content creators everywhere**
