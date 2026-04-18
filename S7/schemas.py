from pydantic import BaseModel, Field 
from typing import Optional, Literal, List
from models import Group

class CreateGroup(BaseModel):
    year_create: int = Field(..., ge=2000)
    number: int = Field(..., ge=1)
    prefix: str
    code: str = Field(pattern=r'^\d{2}\.\d{2}\.\d{2}$')
    class_number: Literal[9, 11]
    tutor_id: Optional[int] = 0
    
    
class PatchGroup(BaseModel):
    tutor_id: int

class Groups(BaseModel):
    id: int
    name: str

class Base(BaseModel):
    year_create: int
    number: int     
    prefix: str  
    code: str = Field(pattern=r'^\d{2}\.\d{2}\.\d{2}$')
    class_number: Literal[9, 11]
    tutor_id: Optional[int] = 0
    name: str            
    count_student: int     
    students: List[int] = []
    
    @classmethod
    def group_to_base(cls, group: Group, group_name: str = None):
        if group_name is None:
            group_name = group.name
    
        return cls(
            year_create=group.year_create,
            number=group.number,
            prefix=group.prefix,
            code=group.code,
            class_number=group.class_number,
            tutor_id=group.tutor_id,
            name=group_name,
            count_student=group.count_student,
            students=[s.id_student for s in group.students]
    )   
    
class GroupFilter(BaseModel):
    course: Optional[int] = None
    count_student: Optional[int] = None
    prefix: Optional[str] = None
    code: Optional[str] = Field(None, pattern=r'^\d{2}\.\d{2}\.\d{2}$')
    class_number: Optional[Literal[9, 11]] = None
    tutor_id: Optional[int] = 0