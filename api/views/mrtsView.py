from pydantic import BaseModel
from typing import List

class MRTResponse(BaseModel):
    data: List[str]



