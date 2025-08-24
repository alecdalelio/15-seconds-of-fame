import os
import logging
import time
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class ViralAnalysis:
    """Data class for viral analysis results."""
    viral_score: float
    emotional_intensity: float
    controversy_level: float
    relatability: float
    educational_value: float
    entertainment_factor: float
    viral_reasoning: str
    clip_title: str
    suggested_caption: str
    combined_score: float

@dataclass
class CostTracker:
    """Track API usage and costs."""
    total_tokens: int = 0
    total_cost: float = 0.0
    requests_made: int = 0
    last_reset: datetime = None
    
    def __post_init__(self):
        if self.last_reset is None:
            self.last_reset = datetime.now()
    
    def add_usage(self, tokens: int, cost: float):
        """Add usage to the tracker."""
        self.total_tokens += tokens
        self.total_cost += cost
        self.requests_made += 1
    
    def get_daily_usage(self) -> Dict[str, Any]:
        """Get daily usage statistics."""
        return {
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "requests_made": self.requests_made,
            "avg_cost_per_request": round(self.total_cost / max(self.requests_made, 1), 4)
        }
    
    def reset_daily(self):
        """Reset daily counters."""
        self.total_tokens = 0
        self.total_cost = 0.0
        self.requests_made = 0
        self.last_reset = datetime.now()

class ViralAnalyzer:
    """OpenAI-powered content analysis for viral potential."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-3.5-turbo"  # Use GPT-3.5 to avoid compatibility issues
        self.max_tokens = 1000  # Limit response size for cost control
        self.cost_tracker = CostTracker()
        self.rate_limit_delay = 0.2  # Reduced delay for better performance
        self.last_request_time = 0
        self.daily_budget = 50.0  # $50 daily budget
        self.enabled = bool(self.api_key)
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.enabled:
            logger.warning("OpenAI API key not found. Using fallback mode.")
        else:
            logger.info(f"OpenAI API key found. Using model: {self.model}")
    
    def analyze_viral_potential(self, transcript: str, segment_info: Dict[str, Any]) -> ViralAnalysis:
        """
        Analyze transcript for viral potential using OpenAI GPT-4.
        
        Args:
            transcript (str): The transcript text to analyze
            segment_info (Dict[str, Any]): Additional segment information
            
        Returns:
            ViralAnalysis: Analysis results with viral potential scores
        """
        if not self.enabled or not transcript.strip():
            return self._fallback_analysis(transcript, segment_info)
        
        # Check budget
        if self.cost_tracker.total_cost >= self.daily_budget:
            logger.warning("Daily budget exceeded. Using fallback mode.")
            return self._fallback_analysis(transcript, segment_info)
        
        try:
            # Rate limiting
            self._respect_rate_limit()
            
            # Prepare the prompt
            prompt = self._create_analysis_prompt(transcript, segment_info)
            
            # Make API call
            response = self._make_api_call(prompt)
            
            if response:
                # Parse the response
                analysis = self._parse_analysis_response(response)
                
                # Track usage (estimate tokens)
                estimated_tokens = len(prompt.split()) + len(response.split())
                estimated_cost = self._estimate_cost(estimated_tokens)
                self.cost_tracker.add_usage(estimated_tokens, estimated_cost)
                
                return analysis
            else:
                return self._fallback_analysis(transcript, segment_info)
                
        except Exception as e:
            logger.error(f"Error in OpenAI analysis: {e}")
            return self._fallback_analysis(transcript, segment_info)
    
    def _create_analysis_prompt(self, transcript: str, segment_info: Dict[str, Any]) -> str:
        """Create the analysis prompt for GPT-4."""
        duration = segment_info.get("end_time", 0) - segment_info.get("start_time", 0)
        
        prompt = f"""
You are an expert content analyst specializing in viral potential assessment. Analyze the following transcript segment for viral potential.

TRANSCRIPT: "{transcript}"
DURATION: {duration:.1f} seconds
START TIME: {segment_info.get('start_time', 0):.1f}s
END TIME: {segment_info.get('end_time', 0):.1f}s

Provide a JSON response with the following structure:
{{
    "viral_score": <1-10, overall viral potential>,
    "emotional_intensity": <1-10, emotional engagement level>,
    "controversy_level": <1-10, likelihood to spark discussion>,
    "relatability": <1-10, universal appeal>,
    "educational_value": <1-10, learning potential>,
    "entertainment_factor": <1-10, pure entertainment value>,
    "viral_reasoning": "<detailed explanation of viral potential>",
    "clip_title": "<catchy, descriptive title for this clip (max 60 chars)>",
    "suggested_caption": "<engaging social media caption with relevant hashtags (max 200 chars)>",
    "combined_score": <1-10, weighted combination>
}}

Scoring guidelines:
- Viral Score: Overall potential to go viral on social media
- Emotional Intensity: How emotionally engaging (joy, surprise, anger, inspiration)
- Controversy Level: Likelihood to spark discussion or debate
- Relatability: Universal appeal and everyday relevance
- Educational Value: Learning potential and insights provided
- Entertainment Factor: Pure entertainment and engagement value

Title guidelines:
- Create a catchy, descriptive title that captures the essence
- Use action words and emotional triggers
- Keep it under 60 characters for social media

Caption guidelines:
- Write an engaging caption that would work on TikTok, Instagram, or LinkedIn
- Include 2-3 relevant hashtags
- Make it shareable and relatable
- Keep it under 200 characters

Keep the viral_reasoning concise but insightful (max 200 words).
Respond with ONLY the JSON object, no additional text.
"""
        return prompt.strip()
    
    def _make_api_call(self, prompt: str) -> Optional[str]:
        """Make the actual API call to OpenAI using requests library."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a viral content analyst. Provide only JSON responses."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.max_tokens,
                "temperature": 0.3
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=15  # Reduced timeout for faster failure detection
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return None
    
    def _parse_analysis_response(self, response: str) -> ViralAnalysis:
        """Parse the JSON response from OpenAI."""
        try:
            data = json.loads(response)
            
            # Extract scores with validation
            viral_score = self._validate_score(data.get("viral_score", 5.0))
            emotional_intensity = self._validate_score(data.get("emotional_intensity", 5.0))
            controversy_level = self._validate_score(data.get("controversy_level", 5.0))
            relatability = self._validate_score(data.get("relatability", 5.0))
            educational_value = self._validate_score(data.get("educational_value", 5.0))
            entertainment_factor = self._validate_score(data.get("entertainment_factor", 5.0))
            
            viral_reasoning = data.get("viral_reasoning", "Analysis not available")
            clip_title = data.get("clip_title", "Viral Clip")
            suggested_caption = data.get("suggested_caption", "Check out this viral moment!")
            
            # Calculate combined score (weighted average)
            combined_score = self._calculate_combined_score(
                viral_score, emotional_intensity, controversy_level,
                relatability, educational_value, entertainment_factor
            )
            
            return ViralAnalysis(
                viral_score=viral_score,
                emotional_intensity=emotional_intensity,
                controversy_level=controversy_level,
                relatability=relatability,
                educational_value=educational_value,
                entertainment_factor=entertainment_factor,
                viral_reasoning=viral_reasoning,
                clip_title=clip_title,
                suggested_caption=suggested_caption,
                combined_score=combined_score
            )
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return self._fallback_analysis("", {})
    
    def _validate_score(self, score: Any) -> float:
        """Validate and normalize a score to 0-10 range."""
        try:
            score = float(score)
            return max(0.0, min(10.0, score))
        except (ValueError, TypeError):
            return 5.0
    
    def _calculate_combined_score(self, viral: float, emotional: float, controversy: float,
                                relatability: float, educational: float, entertainment: float) -> float:
        """Calculate weighted combined score."""
        # Weights for different factors
        weights = {
            'viral': 0.25,
            'emotional': 0.20,
            'controversy': 0.15,
            'relatability': 0.15,
            'educational': 0.10,
            'entertainment': 0.15
        }
        
        combined = (
            viral * weights['viral'] +
            emotional * weights['emotional'] +
            controversy * weights['controversy'] +
            relatability * weights['relatability'] +
            educational * weights['educational'] +
            entertainment * weights['entertainment']
        )
        
        return round(combined, 1)
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on token count."""
        # GPT-3.5 Turbo pricing (approximate)
        input_cost_per_1k = 0.0015  # $0.0015 per 1K input tokens
        output_cost_per_1k = 0.002  # $0.002 per 1K output tokens
        
        # Rough estimate: 70% input, 30% output
        input_tokens = int(tokens * 0.7)
        output_tokens = int(tokens * 0.3)
        
        cost = (input_tokens / 1000 * input_cost_per_1k) + (output_tokens / 1000 * output_cost_per_1k)
        return cost
    
    def _respect_rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _fallback_analysis(self, transcript: str, segment_info: Dict[str, Any]) -> ViralAnalysis:
        """Fallback analysis when OpenAI is unavailable."""
        if not transcript or not transcript.strip():
            return ViralAnalysis(
                viral_score=1.0,
                emotional_intensity=1.0,
                controversy_level=1.0,
                relatability=1.0,
                educational_value=1.0,
                entertainment_factor=1.0,
                viral_reasoning="No transcript available for analysis",
                combined_score=1.0
            )
        
        # Basic fallback scoring based on transcript content
        text = transcript.lower()
        word_count = len(text.split())
        
        # Simple heuristics for fallback scoring
        viral_score = 5.0
        emotional_intensity = 5.0
        controversy_level = 5.0
        relatability = 5.0
        educational_value = 5.0
        entertainment_factor = 5.0
        
        # Adjust based on content indicators
        if any(word in text for word in ["amazing", "incredible", "wow", "crazy", "insane"]):
            viral_score += 1.0
            emotional_intensity += 1.0
        
        if any(word in text for word in ["funny", "hilarious", "joke", "laugh"]):
            entertainment_factor += 1.5
            viral_score += 0.5
        
        if any(word in text for word in ["love", "hate", "best", "worst"]):
            controversy_level += 1.0
            emotional_intensity += 0.5
        
        if word_count > 20:
            educational_value += 0.5
            relatability += 0.5
        
        # Ensure scores are within bounds
        scores = [viral_score, emotional_intensity, controversy_level, 
                 relatability, educational_value, entertainment_factor]
        scores = [max(1.0, min(10.0, score)) for score in scores]
        
        combined_score = self._calculate_combined_score(*scores)
        
        reasoning = "Fallback analysis: Basic content scoring applied due to API unavailability."
        
        # Generate basic title and caption for fallback
        clip_title = "Viral Moment"
        suggested_caption = "Check out this viral moment! #viral #content"
        
        return ViralAnalysis(
            viral_score=scores[0],
            emotional_intensity=scores[1],
            controversy_level=scores[2],
            relatability=scores[3],
            educational_value=scores[4],
            entertainment_factor=scores[5],
            viral_reasoning=reasoning,
            clip_title=clip_title,
            suggested_caption=suggested_caption,
            combined_score=combined_score
        )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return {
            "enabled": self.enabled,
            "daily_usage": self.cost_tracker.get_daily_usage(),
            "daily_budget": self.daily_budget,
            "budget_remaining": max(0, self.daily_budget - self.cost_tracker.total_cost),
            "budget_percentage": (self.cost_tracker.total_cost / self.daily_budget) * 100 if self.daily_budget > 0 else 0
        }
    
    def reset_daily_usage(self):
        """Reset daily usage counters."""
        self.cost_tracker.reset_daily()
    
    def test_api_connection(self) -> bool:
        """Test if the API key is working by making a simple call."""
        if not self.enabled:
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": "Say 'test' and nothing else."}
                ],
                "max_tokens": 10,
                "temperature": 0
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False

# Global analyzer instance
analyzer = ViralAnalyzer()
