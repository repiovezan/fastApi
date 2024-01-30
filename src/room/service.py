from fastapi import Depends
from src.core.logger import ApiLogger

from src.meet.model import Meet
from src.auth.model import User
from src.core.middlewares.error import ApiError
from src.core.database import SessionLocal, get_db
from .model import Position
from .schema import CreateUserPosition, UpdatePosition, ToggleMute



class RoomServices:
  def __init__(self, db: SessionLocal = Depends(get_db)):
    
    self.db = db
  
  def get_room(self, link: str):
    meet = self.__get_meet(link)
    objects = meet.object_meets

    return{
      'link': link,
      'name': meet.name,
      'color': meet.color,
      'objects': objects
    }
  
  def list_users_position(self, link: str):
    meet = self.__get_meet(link)
    return self.db.query(Position).filter(Position.meet_id == meet.id).all()
  
  def delete_user_position(self, client_id: str):
    self.db.query(Position).filter(Position.client_id == client_id).delete()
    self.db.commit()
  
  def update_user_position(self, user_id, link, client_id, dto: UpdatePosition):
    meet = self.__get_meet(link)
    user = self.db.query(User).filter(User.id == user_id).first()

    position = self.db.query(Position).filter(Position.client_id == client_id).one()    
    
    if dto.direction == 'right':
      if position.orientation == 'right':
        if position.x < 7:
          position.x += 1 
      else:
        position.orientation = 'right'
    elif dto.direction == 'left':
      if position.orientation == 'left':
        if position.x > 0:
          position.x -= 1 
      else:
        position.orientation = 'left'
    elif dto.direction == 'up':
      if position.orientation == 'back':
        if position.y > 0:
          position.y -= 1 
      else:
        position.orientation = 'back'
    elif dto.direction == 'down':
      if position.orientation == 'front':
        if position.y < 7:
          position.y += 1 
      else:
        position.orientation = 'front'

    self.db.commit()

  def create_user_position(self, user_id, link, client_id, dto: CreateUserPosition):
    meet = self.__get_meet(link)
    user = self.db.query(User).filter(User.id == user_id).first()
    
    position = Position(
      x = dto.x,
      y = dto.y,
      orientation = dto.orientation,
      user_id = user.id,
      meet_id = meet.id,
      client_id = client_id,
      name = user.name,
      avatar = user.avatar
    )


    users_in_room = self.db.query(Position).filter(Position.meet_id == meet.id).all()

    if len(users_in_room) > 10:
      raise ApiError(message='Meet is full', error='UpdateMeetError', status_code=400)    
    self.db.add(position)
    
    logger = ApiLogger(__name__)
    logger.debug(f'{position}')
    self.db.commit()


  def update_user_mute(self, dto: ToggleMute):
    meet = self.__get_meet(dto.link)
    owner = user = self.db.query(User).filter(User.username == meet.owner).first()
    
    user = self.db.query(User).filter(User.id == dto.user_id).first()

    user_to_mute = self.db.query(User).filter(User.id == dto.user_to_mute).first()

    if (user.id == user_to_mute.id) or (user.id == owner.id):

      self.db.query(Position).filter(Position.meet_id == meet.id).filter(Position.user_id == user_to_mute.id).update({"muted": dto.muted})
      self.db.commit()

  def __get_meet(self, link):
    meet = self.db.query(Meet).filter(Meet.link == link).first()
    if not meet:
      raise ApiError(message='Cannot find this meet', error='Bad Request', status_code=400)
    
    return meet