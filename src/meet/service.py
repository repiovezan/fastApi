from fastapi import Depends
from src.core.database import SessionLocal, get_db

from .model import Meet, ObjectMeet
from .schema import CreateMeet, UpdateMeet


class MeetService:
    def __init__(self, db: SessionLocal = Depends(get_db)):
        self.db = db

    def create_meet(self, create_meet_dto: CreateMeet, username):
        meet = Meet(name=create_meet_dto.name, color=create_meet_dto.color, owner = username)

        self.db.add(meet)
        self.db.commit()
        self.db.refresh(meet)
        return meet

    def get_all_meets(self):
        return self.db.query(Meet).all()

    def get_meet_by_id(self, id: str):
        return self.db.query(Meet).filter(Meet.id == id).one()

    def get_all_meet_objects(self, id: str):
        return self.db.query(Meet).filter(Meet.id == id).one().object_meets

    def update_meet(self, id: str, update_meet_dto: UpdateMeet):
        meet = self.db.query(Meet).filter(Meet.id == id).one()
        
        meet.name = update_meet_dto.name
        meet.color = update_meet_dto.color
        
        self.db.commit()
        self.db.refresh(meet)

        self.db.query(ObjectMeet).filter(ObjectMeet.meet_id == id).delete()
        self.db.commit()

        new_objects = [
            ObjectMeet(
                name=object_meet.name,
                x=object_meet.x,
                y=object_meet.y,
                z_index=object_meet.zindex,
                orientation=object_meet.orientation,
                meet_id=id
            ) for object_meet in update_meet_dto.objects
        ]

        self.db.add_all(new_objects)
        self.db.commit()
        self.db.refresh(meet)

        return {
            **meet.__dict__,
            'objects': [object_meet.__dict__ for object_meet in meet.object_meets]
        }

    def delete_meet(self, id: str):
        meet = self.db.query(Meet).filter(Meet.id == id).one()
        self.db.delete(meet)
        self.db.commit()
        return meet