from datetime import datetime

from typing import List, Dict

from pydantic import BaseModel, Field, conint


class NewBookingInfo(BaseModel):
    date: datetime = Field(
        description="Booking date (YYYY-MM-DD)",
    )
    time: datetime = Field(
        description="Booking start time (HH:MM)",
    )
    hours: conint(ge=1, le=10) = Field(  # type: ignore
        description="Booking hours (from 1 to 10)",
    )
    bikes: List[Dict[str, int]] = Field(
        description="Bikes list: {name: amount}",
    )
