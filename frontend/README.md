# 15 Seconds of Fame - Frontend

A modern React frontend for the 15 Seconds of Fame app that transforms YouTube videos into viral 15-second clips with AI-powered scoring.

## Features

- **YouTube Video Processing**: Submit any YouTube URL for analysis
- **Real-time Processing**: Live status updates during video processing
- **AI-Powered Scoring**: View engagement scores for each 15-second segment
- **Modern UI/UX**: Clean, responsive design with smooth animations
- **Error Handling**: Comprehensive error handling and user feedback
- **Mobile-First**: Fully responsive design that works on all devices

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Query** for API state management
- **Axios** for HTTP requests
- **Heroicons** for icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser to `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
src/
├── components/          # React components
│   ├── VideoProcessor.tsx    # Main video processing form
│   ├── ClipCard.tsx          # Individual clip display
│   ├── ProcessingStatus.tsx  # Loading and status display
│   ├── ScoreDisplay.tsx      # Visual score representation
│   └── ErrorMessage.tsx      # Error display component
├── hooks/              # Custom React hooks
│   ├── useVideoProcessing.ts # Video processing hook
│   └── useApi.ts            # Generic API hook
├── services/           # API services
│   └── api.ts              # Backend communication
├── types/              # TypeScript type definitions
│   └── api.ts              # API request/response types
└── utils/              # Utility functions
    └── validation.ts        # URL validation helpers
```

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`:

- `GET /` - Health check
- `POST /process` - Process YouTube video into scored clips

### Environment Configuration

Create a `.env` file in the frontend directory:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Usage

1. **Enter YouTube URL**: Paste any YouTube video URL into the input field
2. **Process Video**: Click "Process Video" to start analysis
3. **View Results**: See scored clips sorted by engagement potential
4. **Analyze Scores**: Each clip shows:
   - Engagement score (0-10 scale)
   - Time range (start - end)
   - Transcript preview
   - Reasoning for the score

## Testing

Use this test URL to verify functionality:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## Development

### Adding New Features

1. **New Components**: Add to `src/components/`
2. **API Integration**: Extend `src/services/api.ts`
3. **Custom Hooks**: Add to `src/hooks/`
4. **Types**: Update `src/types/api.ts`

### Styling

- Use Tailwind CSS classes for styling
- Custom components defined in `src/index.css`
- Responsive design with mobile-first approach

### State Management

- React Query for server state (API calls)
- React useState for local component state
- No global state management needed for MVP

## Troubleshooting

### Common Issues

1. **Backend Connection**: Ensure backend is running on port 8000
2. **CORS Issues**: Backend should allow requests from `http://localhost:5173`
3. **Build Errors**: Check TypeScript types and imports

### Development Tips

- Use React DevTools for debugging
- Check browser console for API errors
- Monitor network tab for request/response details

## Contributing

1. Follow TypeScript best practices
2. Use functional components with hooks
3. Maintain responsive design
4. Add proper error handling
5. Test on mobile devices

## License

This project is part of the 15 Seconds of Fame application.
