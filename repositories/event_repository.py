from datetime import date
from typing import List, Optional
from sqlalchemy import func

from models.event import Event, EventSchema, EventCreateDto
from repositories.abstract_repository import AbstractRepository


class EventRepository(AbstractRepository):
    def create(self, event_data: EventCreateDto) -> EventSchema:
        event = Event(**event_data.model_dump())
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return EventSchema.model_validate(event)
    
    def get_by_id(self, event_id: int) -> Optional[EventSchema]:
        event = self.db.query(Event).filter(Event.id == event_id).first()
        return EventSchema.model_validate(event) if event else None
    
    def get_by_user_id(self, user_id: int) -> List[EventSchema]:
        events = self.db.query(Event).filter(Event.user_id == user_id).all()
        return [EventSchema.model_validate(event) for event in events]
    
    def get_by_user_id_and_date(self, user_id: int, day: date) -> List[EventSchema]:
        events = self.db.query(Event).filter(
            Event.user_id == user_id,
            func.date(Event.start_time) == day
        ).all()
        return [EventSchema.model_validate(event) for event in events]
    
    def delete(self, event_id: int) -> None:
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if event:
            self.db.delete(event)
            self.db.commit()