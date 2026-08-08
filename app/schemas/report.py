# Validation of the data entered
from pydantic import BaseModel, UUID4, ConfigDict
# BaseModel is used for data validation and serialization
from datetime import datetime
from typing import Optional

# Base schema used for shared fields
class ReportBase(BaseModel):
    description: str
    lat: Optional[float] =None
    lng: Optional[float] =None

    #__init__ isn't required since we are using pydantic

# Used when creating a report
class ReportCreate(ReportBase):
    description: str
    lat: float
    lng: float
    category: Optional[str] = None

# Used when updating a report
class ReportUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    priority_score: Optional[float] = None

# Used for response output
class ReportResponse(ReportBase):
    id: UUID4
    description: str
    category: Optional[str]
    priority_score: Optional[float]
    status: str
    created_at: datetime
    lat: Optional[float]
    lng: Optional[float]
    image_path: Optional[str]

    model_config = ConfigDict(
        from_attributes=True
    )