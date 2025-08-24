import librosa
import numpy as np
import logging
from typing import List, Dict, Any, Tuple
from scipy.signal import find_peaks
from pathlib import Path

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        
    def analyze_audio_waveform(self, audio_path: str) -> Dict[str, Any]:
        """Extract comprehensive audio features and detect patterns."""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Extract various audio features
            features = {
                'audio_data': y,
                'sample_rate': sr,
                'duration': duration,
                'rms_energy': librosa.feature.rms(y=y)[0],
                'spectral_centroid': librosa.feature.spectral_centroid(y=y, sr=sr)[0],
                'zero_crossing_rate': librosa.feature.zero_crossing_rate(y)[0],
                'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13),
                'tempo': librosa.beat.tempo(y=y, sr=sr)[0]
            }
            
            logger.info(f"Audio analysis completed for {audio_path}")
            return features
            
        except Exception as e:
            logger.error(f"Error analyzing audio waveform: {e}")
            return None
    
    def detect_silence_segments(self, audio_data: np.ndarray, threshold: float = 0.01, 
                               min_silence_duration: float = 0.5) -> List[Tuple[float, float]]:
        """Find natural pauses and speech boundaries."""
        try:
            # Calculate RMS energy
            rms = librosa.feature.rms(y=audio_data)[0]
            
            # Find silence regions (energy below threshold)
            silence_mask = rms < threshold
            
            # Convert to time domain
            frame_length = 2048
            hop_length = 512
            time_stamps = librosa.frames_to_time(np.arange(len(rms)), sr=self.sample_rate, 
                                               hop_length=hop_length, n_fft=frame_length)
            
            # Find silence segments
            silence_segments = []
            in_silence = False
            silence_start = 0
            
            for i, (is_silent, time) in enumerate(zip(silence_mask, time_stamps)):
                if is_silent and not in_silence:
                    silence_start = time
                    in_silence = True
                elif not is_silent and in_silence:
                    silence_end = time
                    silence_duration = silence_end - silence_start
                    
                    if silence_duration >= min_silence_duration:
                        silence_segments.append((silence_start, silence_end))
                    
                    in_silence = False
            
            # Handle case where audio ends in silence
            if in_silence:
                silence_end = time_stamps[-1]
                silence_duration = silence_end - silence_start
                if silence_duration >= min_silence_duration:
                    silence_segments.append((silence_start, silence_end))
            
            logger.info(f"Detected {len(silence_segments)} silence segments")
            return silence_segments
            
        except Exception as e:
            logger.error(f"Error detecting silence segments: {e}")
            return []
    
    def detect_volume_spikes(self, audio_data: np.ndarray, threshold_percentile: float = 85) -> List[float]:
        """Identify dramatic/exciting moments based on volume spikes."""
        try:
            # Calculate RMS energy
            rms = librosa.feature.rms(y=audio_data)[0]
            
            # Find peaks above threshold
            threshold = np.percentile(rms, threshold_percentile)
            peaks, _ = find_peaks(rms, height=threshold, distance=int(self.sample_rate * 0.5))  # Min 0.5s apart
            
            # Convert peak indices to time
            frame_length = 2048
            hop_length = 512
            peak_times = librosa.frames_to_time(peaks, sr=self.sample_rate, 
                                              hop_length=hop_length, n_fft=frame_length)
            
            logger.info(f"Detected {len(peak_times)} volume spikes")
            return peak_times.tolist()
            
        except Exception as e:
            logger.error(f"Error detecting volume spikes: {e}")
            return []
    
    def calculate_audio_quality_score(self, audio_data: np.ndarray) -> float:
        """Score audio quality based on clarity and noise levels."""
        try:
            # Calculate signal-to-noise ratio approximation
            rms = librosa.feature.rms(y=audio_data)[0]
            signal_power = np.mean(rms ** 2)
            noise_power = np.var(rms)
            
            if noise_power == 0:
                snr = 100
            else:
                snr = 10 * np.log10(signal_power / noise_power)
            
            # Normalize to 1-10 scale
            quality_score = min(10, max(1, (snr + 20) / 10))
            
            return quality_score
            
        except Exception as e:
            logger.error(f"Error calculating audio quality score: {e}")
            return 5.0  # Default middle score
    
    def calculate_dramatic_intensity(self, audio_data: np.ndarray, start_time: float, end_time: float) -> float:
        """Calculate dramatic intensity for a specific time segment."""
        try:
            start_frame = int(start_time * self.sample_rate)
            end_frame = int(end_time * self.sample_rate)
            segment_data = audio_data[start_frame:end_frame]
            
            if len(segment_data) == 0:
                return 1.0
            
            # Calculate various intensity metrics
            rms = librosa.feature.rms(y=segment_data)[0]
            spectral_centroid = librosa.feature.spectral_centroid(y=segment_data, sr=self.sample_rate)[0]
            
            # Volume variation (excitement)
            volume_variation = np.std(rms) / (np.mean(rms) + 1e-8)
            
            # Spectral variation (voice changes, emphasis)
            spectral_variation = np.std(spectral_centroid) / (np.mean(spectral_centroid) + 1e-8)
            
            # Peak volume (dramatic moments)
            peak_volume = np.max(rms)
            
            # Combine metrics into intensity score
            intensity = (volume_variation * 0.4 + spectral_variation * 0.3 + peak_volume * 0.3)
            
            # Normalize to 1-10 scale
            intensity_score = min(10, max(1, intensity * 5))
            
            return intensity_score
            
        except Exception as e:
            logger.error(f"Error calculating dramatic intensity: {e}")
            return 5.0
    
    def find_optimal_segments(self, audio_path: str, min_duration: float = 10.0, 
                            max_duration: float = 20.0) -> List[Dict[str, Any]]:
        """Main function that returns intelligent clip boundaries."""
        try:
            # Analyze audio
            features = self.analyze_audio_waveform(audio_path)
            if not features:
                return []
            
            audio_data = features['audio_data']
            duration = features['duration']
            
            # Detect silence segments and volume spikes
            silence_segments = self.detect_silence_segments(audio_data)
            volume_spikes = self.detect_volume_spikes(audio_data)
            
            # Generate potential segment boundaries
            potential_boundaries = []
            
            # Add silence-based boundaries
            for start, end in silence_segments:
                potential_boundaries.append((start, 'silence'))
                potential_boundaries.append((end, 'silence'))
            
            # Add volume spike boundaries
            for spike_time in volume_spikes:
                potential_boundaries.append((spike_time, 'spike'))
            
            # Sort boundaries by time
            potential_boundaries.sort(key=lambda x: x[0])
            
            # Generate optimal segments
            segments = []
            current_start = 0
            
            for boundary_time, boundary_type in potential_boundaries:
                if boundary_time <= current_start:
                    continue
                
                segment_duration = boundary_time - current_start
                
                # Check if segment meets duration requirements
                if min_duration <= segment_duration <= max_duration:
                    # Calculate segment scores
                    audio_quality = self.calculate_audio_quality_score(
                        audio_data[int(current_start * self.sample_rate):int(boundary_time * self.sample_rate)]
                    )
                    
                    dramatic_intensity = self.calculate_dramatic_intensity(
                        audio_data, current_start, boundary_time
                    )
                    
                    # Calculate speech clarity (simplified)
                    segment_data = audio_data[int(current_start * self.sample_rate):int(boundary_time * self.sample_rate)]
                    zcr = librosa.feature.zero_crossing_rate(segment_data)[0]
                    speech_clarity = min(10, max(1, 10 - np.mean(zcr) * 100))
                    
                    # Calculate segment coherence (based on boundary type)
                    coherence = 8.0 if boundary_type == 'silence' else 6.0
                    
                    segment = {
                        'start_time': current_start,
                        'end_time': boundary_time,
                        'duration': segment_duration,
                        'audio_quality_score': round(audio_quality, 1),
                        'dramatic_intensity': round(dramatic_intensity, 1),
                        'speech_clarity': round(speech_clarity, 1),
                        'segment_coherence': round(coherence, 1),
                        'boundary_type': boundary_type
                    }
                    
                    segments.append(segment)
                
                current_start = boundary_time
            
            # Handle final segment if needed
            if current_start < duration:
                final_duration = duration - current_start
                if min_duration <= final_duration <= max_duration:
                    audio_quality = self.calculate_audio_quality_score(
                        audio_data[int(current_start * self.sample_rate):]
                    )
                    dramatic_intensity = self.calculate_dramatic_intensity(
                        audio_data, current_start, duration
                    )
                    
                    segment_data = audio_data[int(current_start * self.sample_rate):]
                    zcr = librosa.feature.zero_crossing_rate(segment_data)[0]
                    speech_clarity = min(10, max(1, 10 - np.mean(zcr) * 100))
                    
                    segment = {
                        'start_time': current_start,
                        'end_time': duration,
                        'duration': final_duration,
                        'audio_quality_score': round(audio_quality, 1),
                        'dramatic_intensity': round(dramatic_intensity, 1),
                        'speech_clarity': round(speech_clarity, 1),
                        'segment_coherence': 7.0,
                        'boundary_type': 'end'
                    }
                    
                    segments.append(segment)
            
            # Sort segments by overall quality score
            for segment in segments:
                segment['overall_score'] = (
                    segment['audio_quality_score'] * 0.2 +
                    segment['dramatic_intensity'] * 0.4 +
                    segment['speech_clarity'] * 0.2 +
                    segment['segment_coherence'] * 0.2
                )
            
            segments.sort(key=lambda x: x['overall_score'], reverse=True)
            
            logger.info(f"Generated {len(segments)} optimal segments from {audio_path}")
            return segments
            
        except Exception as e:
            logger.error(f"Error finding optimal segments: {e}")
            return []

# Global analyzer instance
audio_analyzer = AudioAnalyzer()
