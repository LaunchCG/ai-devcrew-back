from pydantic import BaseModel
from typing import List, Optional

class StoryReview(BaseModel):
    story: str
    validation: str
    issues: List[str]
    suggestions: List[str]
    acceptance_criteria_check: Optional[str] = None
    qa_testability: Optional[str] = None
