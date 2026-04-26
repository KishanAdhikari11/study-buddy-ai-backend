from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from utils.logger import get_logger

logger = get_logger()

ytt_api = YouTubeTranscriptApi()


def transcribe_yt(video_id: str) -> list[dict[str, str | float]]:
    try:
        transcript = ytt_api.fetch(video_id, languages=["en"])
        return transcript.to_raw_data()
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        logger.error(
            "Error fetching transcript: ", extra={"error": str(e), "video_id": video_id}
        )
        return []
