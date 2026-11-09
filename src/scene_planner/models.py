from pydantic import BaseModel
from typing import List


class Scene(BaseModel):
    scene_number: int
    narration: str
    visual_description: str


class ScenePlan(BaseModel):
    scenes: List[Scene]


class SceneGroup(BaseModel):
    sentences: List[int]
    visual_description: str


class SceneGrouping(BaseModel):
    scenes: List[SceneGroup]


class SceneVisual(BaseModel):
    scene_number: int
    visual_description: str


class SceneVisualPlan(BaseModel):
    scenes: List[SceneVisual]