from pydantic import BaseModel

class CommentCreate(BaseModel):
    anime_id: int
    text: str
    tagged_user_id: str | None = None