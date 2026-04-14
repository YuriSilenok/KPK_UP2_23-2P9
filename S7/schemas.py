from pydantic import BaseModel, Field 
from typing import Optional, Literal, List

class CreateGroup(BaseModel):
    year_create: int = Field(..., ge=2000)
    number: int = Field(..., ge=1)
    prefix: str
    code: str = Field(pattern=r'^\d{2}\.\d{2}\.\d{2}$')
    class_number: Literal[9, 11]
    tutor_id: Optional[int] = None
    
    
class PatchGroup(BaseModel):
    tutor_id: int

class InfoGroup(BaseModel):
    number_course: int
    count_student: int
    prefix: str
    code: str = Field(pattern=r'^\d{2}\.\d{2}\.\d{2}$')
    class_number: Literal[9, 11]
    tutor_id: Optional[int] = 0
    
class Info_Id(BaseModel):
    year_create: int
    number: int     
    prefix: str  
    code: str = Field(pattern=r'^\d{2}\.\d{2}\.\d{2}$')
    class_number: Literal[9, 11]
    tutor_id: Optional[int] = None 
    name: str            
    count_student: int     
    students: List[int] = [] 