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
