from pydantic import BaseModel
from typing import List

class AnimeRecommendation(BaseModel):
    id: int
    title_english: str
    similarity: float

class RecommendationResponse(BaseModel):
    query: str
    results: List[AnimeRecommendation]
    processing_time_ms: float

class SimilarByIdResponse(BaseModel):
    anime_id: int
    recommendations: List[AnimeRecommendation]
    processing_time_ms: float

