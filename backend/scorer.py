from typing import List, Dict, Any
import re
from viral_analyzer import analyzer

def score_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Score transcript segments based on engagement potential and viral analysis.
    
    Args:
        segments (List[Dict[str, Any]]): List of video segments with transcripts
        
    Returns:
        List[Dict[str, Any]]: List of scored clips with rankings
    """
    print(f"Scoring {len(segments)} segments with OpenAI viral analysis")
    
    scored_clips = []
    
    for segment in segments:
        # Get OpenAI viral analysis
        viral_analysis = analyzer.analyze_viral_potential(
            segment.get("transcript", ""), 
            segment
        )
        
        # Calculate combined score using both traditional and viral analysis
        combined_score = calculate_enhanced_score(
            segment.get("transcript", ""), 
            viral_analysis
        )
        
        scored_clip = {
            "id": f"clip_{segment['id']}",
            "segment_id": segment["id"],
            "score": combined_score,
            "start_time": segment["start_time"],
            "end_time": segment["end_time"],
            "transcript": segment.get("transcript", ""),
            "audio_path": segment.get("audio_path", ""),
            "video_path": segment.get("video_path", ""),
            "reasoning": viral_analysis.viral_reasoning,
            # Viral analysis scores
            "viral_score": viral_analysis.viral_score,
            "emotional_intensity": viral_analysis.emotional_intensity,
            "controversy_level": viral_analysis.controversy_level,
            "relatability": viral_analysis.relatability,
            "educational_value": viral_analysis.educational_value,
            "entertainment_factor": viral_analysis.entertainment_factor,
            "combined_score": viral_analysis.combined_score,
            # API usage tracking
            "api_usage_tokens": getattr(viral_analysis, 'api_usage_tokens', 0),
            "api_usage_cost": getattr(viral_analysis, 'api_usage_cost', 0.0)
        }
        
        scored_clips.append(scored_clip)
    
    # Sort by combined score (highest first)
    scored_clips.sort(key=lambda x: x["combined_score"], reverse=True)
    
    return scored_clips

def calculate_enhanced_score(transcript: str, viral_analysis) -> float:
    """
    Calculate enhanced score combining traditional and viral analysis.
    
    Args:
        transcript (str): The transcript text to analyze
        viral_analysis: OpenAI viral analysis results
        
    Returns:
        float: Enhanced score between 0 and 10
    """
    if not transcript or transcript.strip() == "":
        return 0.0
    
    # Get traditional engagement score
    traditional_score = calculate_engagement_score(transcript)
    
    # Get viral analysis combined score
    viral_score = viral_analysis.combined_score
    
    # Weight the scores (70% viral analysis, 30% traditional)
    enhanced_score = (viral_score * 0.7) + (traditional_score * 0.3)
    
    return round(enhanced_score, 1)

def calculate_engagement_score(transcript: str) -> float:
    """
    Calculate engagement score based on transcript content.
    
    Args:
        transcript (str): The transcript text to analyze
        
    Returns:
        float: Score between 0 and 10
    """
    if not transcript or transcript.strip() == "":
        return 0.0
    
    score = 5.0  # Base score
    
    # Convert to lowercase for analysis
    text = transcript.lower()
    
    # Positive indicators
    positive_words = [
        "amazing", "incredible", "wow", "awesome", "fantastic", "brilliant",
        "hilarious", "funny", "joke", "laugh", "haha", "lol", "omg",
        "crazy", "insane", "unbelievable", "shocking", "controversial",
        "love", "hate", "best", "worst", "perfect", "terrible"
    ]
    
    # Negative indicators
    negative_words = [
        "boring", "dull", "quiet", "silence", "um", "uh", "like", "you know"
    ]
    
    # Count positive words
    positive_count = sum(1 for word in positive_words if word in text)
    score += positive_count * 0.5
    
    # Count negative words
    negative_count = sum(1 for word in negative_words if word in text)
    score -= negative_count * 0.3
    
    # Bonus for exclamation marks (excitement)
    exclamation_count = text.count("!")
    score += exclamation_count * 0.2
    
    # Bonus for question marks (engagement)
    question_count = text.count("?")
    score += question_count * 0.1
    
    # Bonus for longer transcripts (more content)
    word_count = len(text.split())
    if word_count > 20:
        score += 0.5
    elif word_count < 5:
        score -= 1.0
    
    # Ensure score is between 0 and 10
    score = max(0.0, min(10.0, score))
    
    return round(score, 1)

def generate_reasoning(transcript: str, score: float) -> str:
    """
    Generate reasoning for the score based on transcript content.
    
    Args:
        transcript (str): The transcript text
        score (float): The calculated score
        
    Returns:
        str: Reasoning for the score
    """
    if not transcript or transcript.strip() == "":
        return "No transcript available"
    
    text = transcript.lower()
    word_count = len(text.split())
    
    reasons = []
    
    if score >= 8.0:
        reasons.append("High engagement potential")
    elif score >= 6.0:
        reasons.append("Good content quality")
    elif score >= 4.0:
        reasons.append("Moderate engagement potential")
    else:
        reasons.append("Low engagement potential")
    
    # Add specific observations
    if any(word in text for word in ["funny", "hilarious", "joke", "laugh"]):
        reasons.append("Contains humor")
    
    if any(word in text for word in ["amazing", "incredible", "wow"]):
        reasons.append("Expresses excitement")
    
    if text.count("!") > 2:
        reasons.append("High energy/excitement")
    
    if word_count > 20:
        reasons.append("Substantial content")
    elif word_count < 5:
        reasons.append("Very short content")
    
    return "; ".join(reasons) if reasons else "Standard content"
