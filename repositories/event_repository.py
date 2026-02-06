from datetime import date, timedelta
from typing import List

from sqlalchemy import func
from models.event import Event, EventCreateDto, EventSchema
from repositories.abstract_repository import AbstractRepository


class EventRepository(AbstractRepository):
    def create(self, event_data: EventCreateDto) -> EventSchema:
        event = Event(**event_data.model_dump())
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return EventSchema.model_validate(event, from_attributes=True)
    
    def get_by_id(self, event_id: int) -> EventSchema | None:
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if event is None:
            return None
        return EventSchema.model_validate(event, from_attributes=True)
    
    def get_by_user_id(self, user_id: int) -> List[EventSchema]:
        return [
            EventSchema.model_validate(event, from_attributes=True)
            for event in self.db.query(Event).filter(
                Event.user_id == user_id
            ).all()
        ]
    
    def get_by_user_id_and_date(self, user_id: int, day: date) -> List[EventSchema]:
        return [
            EventSchema.model_validate(event, from_attributes=True)
            for event in self.db.query(Event).filter(
                Event.user_id == user_id,
                func.date(Event.start_time) == day
            ).all()
        ]
    
    def delete(self, event_id: int) -> None:
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if event is None:
            return None
        self.db.delete(event)
        self.db.commit()