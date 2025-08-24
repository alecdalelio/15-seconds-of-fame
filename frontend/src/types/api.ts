export interface ProcessVideoRequest {
  youtube_url: string;
}

export interface Clip {
  id: string;
  segment_id: string;
  score: number;
  start_time: number;
  end_time: number;
  transcript: string;
  audio_path: string;
  video_path: string;
  reasoning: string;
  // Viral analysis scores
  viral_score?: number;
  emotional_intensity?: number;
  controversy_level?: number;
  relatability?: number;
  educational_value?: number;
  entertainment_factor?: number;
  combined_score?: number;
  // API usage tracking
  api_usage_tokens?: number;
  api_usage_cost?: number;
}

export interface ProcessVideoResponse {
  clips: Clip[];
  status: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface HealthCheckResponse {
  message: string;
}
