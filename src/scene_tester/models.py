from pydantic import BaseModel
from typing import List, Literal


class SceneIssue(BaseModel):
    scene_number: int
    severity: Literal["CRITICAL", "MINOR"]
    issue: str
    explanation: str
    suggested_fix: str


class SceneReview(BaseModel):
    passed: bool
    issues: List[SceneIssue]
    overall_feedback: str