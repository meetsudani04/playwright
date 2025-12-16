from pydantic import BaseModel
from datetime import datetime

# User Schemas
class LoginData(BaseModel):
    username: str
    password: str

class SlackUserData(BaseModel):
    slack_id: str
    name: str
    hrms_username: str
    hrms_password: str
    trigger_time: str

class SlackUserResponse(BaseModel):
    id: int
    slack_id: str
    name: str
    hrms_username: str
    trigger_time: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True