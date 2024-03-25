from pydantic import BaseModel
from typing import Literal
from enum import Enum

class Status(str, Enum):
    OK = "OK"
    NOT_OK = "NOT OK"

class Health(BaseModel):
    app_status: Status | None
    db_status: Status | None
