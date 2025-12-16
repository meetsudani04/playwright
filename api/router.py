import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.schema import LoginData, SlackUserData, SlackUserResponse
from db.database import get_db
from db.models import SlackUser
from services.automation import HRMAutomation

router = APIRouter()

@router.post("/run-selenium")
async def run_selenium_endpoint(data: LoginData):
    automation = HRMAutomation(
        username=data.username,
        password=data.password,
    )
    return await automation.run_async()

@router.post("/slack-users", response_model=SlackUserResponse)
async def create_slack_user(data: SlackUserData, db: Session = Depends(get_db)):
    # Check if slack_id already exists
    existing_user = db.query(SlackUser).filter(SlackUser.slack_id == data.slack_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Slack user already exists")
    
    # Create new SlackUser instance
    new_user = SlackUser(
        name=data.name,
        slack_id=data.slack_id,
        hrms_username=data.hrms_username,
        hrms_password=data.hrms_password,
        trigger_time=data.trigger_time
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/slack-users", response_model=list[SlackUserResponse])
async def get_all_slack_users(db: Session = Depends(get_db)):
    users = db.query(SlackUser).all()
    return users

@router.get("/slack-users/{id}", response_model=SlackUserResponse)
async def get_slack_user(id: int, db: Session = Depends(get_db)):
    user = db.query(SlackUser).filter(SlackUser.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Slack user not found")
    return user

@router.put("/slack-users/{id}", response_model=SlackUserResponse)
async def update_slack_user(id: int, data: SlackUserData, db: Session = Depends(get_db)):
    """
    Update an existing Slack user entry
    """
    user = db.query(SlackUser).filter(SlackUser.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Slack user not found")
    
    try:
        user.slack_id = data.slack_id
        user.name = data.name
        user.hrms_username = data.hrms_username
        user.hrms_password = data.hrms_password
        user.trigger_time = data.trigger_time
        
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")