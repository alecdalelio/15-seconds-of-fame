# 15 Seconds of Fame

A web application that analyzes YouTube videos to find the most viral 15-second clips using AI-powered analysis and machine learning.

## 🎯 Overview

15 Seconds of Fame automatically processes YouTube videos to identify the most engaging and shareable 15-second segments. The application uses advanced AI analysis to score video segments based on viral potential, helping content creators optimize their content for maximum engagement.

## ✨ Features

- **Smart Video Segmentation**: Automatically splits videos into optimal 15-second clips
- **AI-Powered Analysis**: Uses OpenAI's GPT models to analyze content virality
- **Viral Scoring**: Scores each clip based on engagement potential
- **Audio Analysis**: Advanced audio processing for better clip selection
- **Real-time Processing**: Fast video processing with progress tracking
- **Modern Web Interface**: Clean, responsive React frontend

## 🏗️ Architecture

This is a monorepo containing:

- **Frontend**: React + TypeScript + Vite application
- **Backend**: FastAPI + Python serverless functions
- **AI Analysis**: OpenAI GPT integration for content analysis
- **Audio Processing**: Custom audio segmentation algorithms

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
├── frontend/                    # React + Vite frontend
│   ├── src/                    # Source code
│   ├── dist/                   # Build output
│   └── package.json           # Frontend dependencies
├── backend/                    # FastAPI + Python backend
│   ├── app.py                 # Main FastAPI application
│   ├── viral_analyzer.py      # Viral analysis logic
│   ├── openai_analyzer.py     # OpenAI integration
│   ├── clipper.py             # Video processing
│   ├── audio_analyzer.py      # Audio analysis
│   ├── scorer.py              # Scoring algorithms
│   ├── database.py            # Database operations
│   └── requirements.txt       # Python dependencies
├── vercel.json                # Vercel deployment config
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🚀 Deployment

This project is configured for deployment on Vercel:

- **Frontend**: Automatically built and served as a static SPA
- **Backend**: Deployed as serverless functions
- **Environment Variables**: Configure `OPENAI_API_KEY` in Vercel dashboard

### Deployment Configuration

The `vercel.json` file configures:
- Build command: `cd frontend && npm install && npm run build`
- Output directory: `frontend/dist`
- SPA routing: All routes serve `index.html`
- Python runtime: 3.9 for backend functions

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
- [Phase 2 Implementation](./PHASE2_IMPLEMENTATION_SUMMARY.md) - Recent feature updates

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

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- FastAPI for the excellent web framework
- React and Vite for the modern frontend experience
- Vercel for seamless deployment

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Built with ❤️ for content creators everywhere**
