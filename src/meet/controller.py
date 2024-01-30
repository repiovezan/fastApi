from fastapi import APIRouter, Body, Depends

from src.auth.handler import get_current_user

from .schema import CreateMeet, UpdateMeet
from .service import MeetService


router = APIRouter()

@router.post('/')
async def create_meet(create_meet_dto: 
    CreateMeet, service: MeetService = Depends(MeetService), 
    username: str = Depends(get_current_user)):
    return service.create_meet(create_meet_dto, username)

@router.get('/')
async def get_all_meets(service: MeetService = Depends(MeetService), username: str = Depends(get_current_user)):
    return service.get_all_meets()

@router.put('/{id}')
async def update_meet(
    id: str, 
    update_meet_dto: UpdateMeet = Body(embed=False), 
    username: str = Depends(get_current_user), 
    service: MeetService = Depends(MeetService)):
    return service.update_meet(id, update_meet_dto)

@router.delete('/{id}')
async def delete_meet(id: str, service: MeetService = Depends(MeetService), username: str = Depends(get_current_user)):
    return service.delete_meet(id)

@router.get('/{id}')
async def get_all_meet_objects(id: str, service: MeetService = Depends(MeetService), username: str = Depends(get_current_user)):
    return service.get_meet_by_id(id)

@router.get('/{id}/object')
async def get_all_meet_objects(id: str, service: MeetService = Depends(MeetService), username: str = Depends(get_current_user)):
    return service.get_all_meet_objects(id)