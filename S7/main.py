from fastapi import FastAPI, Depends, HTTPException
from schemas import CreateGroup, PatchGroup, InfoGroup, Info_Id
from database import get_db
from models import Group
from crud import (
create_group as create,
patch_group as patch,
delete_group as delete,
info_id as info
)

app = FastAPI()


@app.post('/groups') # создать группу
def create_group(group: CreateGroup, db=Depends(get_db)):
    try:
        result = create(**group.dict())
        return {"id": result.id, "status": "created"}
    except Exception as e:
        raise HTTPException(400, detail=(e))

@app.patch('/groups/{group_id}') # изменить группу по ID
def patch_group(group_id: int, group: PatchGroup, db=Depends(get_db)):
    try:
        result = patch(group_id, **group.dict())
        if result is False:
            raise HTTPException(404, detail="Group not found")
        return {**result}
    except Exception as e:
        raise HTTPException(400, detail=e)

@app.delete('/groups/{group_id}') # удалить группу по ID
def delete_group(group_id: int, db=Depends(get_db)):
    try:
        result = delete(group_id)
        if not result:
            raise HTTPException(404, detail='Group not found')
        return {"status": "True"}
    except Exception as e:
        raise HTTPException(400, detail=(e))

@app.get('/groups/{group_id}') # получить группу по ID
def info_id(group: Info_Id, db=Depends(get_db)):
    pass
@app.get('/groups') # получить группы
def info(group: InfoGroup, db=Depends(get_db)):
    pass