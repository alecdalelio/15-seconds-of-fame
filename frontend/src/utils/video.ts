/**
 * Extract video ID from YouTube URL
 */
export const extractVideoId = (url: string): string | null => {
  try {
    const urlObj = new URL(url);
    if (urlObj.hostname.includes('youtube.com') || urlObj.hostname.includes('youtu.be')) {
      if (urlObj.hostname.includes('youtu.be')) {
        return urlObj.pathname.slice(1);
      }
      return urlObj.searchParams.get('v');
    }
    return null;
  } catch {
    return null;
  }
};

/**
 * Format video title for display
 */
export const formatVideoTitle = (title: string, url?: string): string => {
  if (title && title !== 'Unknown Video') {
    return title;
  }
  
  if (url) {
    const videoId = extractVideoId(url);
    if (videoId) {
      return `YouTube Video (${videoId.substring(0, 8)}...)`;
    }
  }
  
  return 'Unknown Video';
};

/**
 * Get a short video identifier for display
 */
export const getVideoIdentifier = (title: string, url?: string): string => {
  if (title && title !== 'Unknown Video') {
    // Truncate long titles
    return title.length > 50 ? title.substring(0, 47) + '...' : title;
  }
  
  if (url) {
    const videoId = extractVideoId(url);
    if (videoId) {
      return `Video (${videoId.substring(0, 8)}...)`;
    }
  }
  
  return 'Unknown Video';
};
