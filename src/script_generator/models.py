from pydantic import BaseModel


class ScriptDraft(BaseModel):
    title: str
    topic: str
    hook: str
    full_script: str
    takeaway: str