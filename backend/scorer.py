from typing import List, Dict, Any
import re

def score_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Score transcript segments based on engagement potential.
    
    Args:
        segments (List[Dict[str, Any]]): List of video segments with transcripts
        
    Returns:
        List[Dict[str, Any]]: List of scored clips with rankings
    """
    print(f"Scoring {len(segments)} segments")
    
    scored_clips = []
    
    for segment in segments:
        # Basic scoring based on transcript content
        score = calculate_engagement_score(segment.get("transcript", ""))
        
        scored_clip = {
            "id": f"clip_{segment['id']}",
            "segment_id": segment["id"],
            "score": score,
            "start_time": segment["start_time"],
            "end_time": segment["end_time"],
            "transcript": segment.get("transcript", ""),
            "audio_path": segment.get("audio_path", ""),
            "video_path": segment.get("video_path", ""),
            "reasoning": generate_reasoning(segment.get("transcript", ""), score)
        }
        
        scored_clips.append(scored_clip)
    
    # Sort by score (highest first)
    scored_clips.sort(key=lambda x: x["score"], reverse=True)
    
    return scored_clips

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
