from fastapi import FastAPI
from models import Group
from pydantic import BaseModel, Field
from typing import Optional, Literal

app = FastAPI()

class CreateGroup(BaseModel):
    year_create: int = Field(..., ge=2000)
    number: int = Field(..., ge=1)
    prefix: str
    code: str
    class_nubmer: Literal[9, 11]
    tutor_id: Optional[int] = None
    
class 
    

@app.post('/groups') # создать группу
def create_group(group: CreateGroup):
    pass
@app.patch('/groups/{group_id}') # изменить группу по ID
def patch_group():
    pass
@app.delete('/groups/{group_id}') # удалить группу по ID
def delet_group():
    pass
@app.get('/groups/{group_id}') # получить группу по ID
def info_id():
    pass
@app.get('/groups') # получить группы
def info():
    pass