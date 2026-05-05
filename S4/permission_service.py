from fastapi import Depends, HTTPException, APIRouter, Request
from peewee import DoesNotExist
from models import Permission
from check_permission import check_permission

async def require_permission(request: Request):
    answer = await check_permission(role_id = 1, method = str(request.method), url = str(request.url.path))
    if answer["status_code"] == 200:
        answer.pop("status_code")
        return answer
    else:
        answer.pop("status_code")
        raise HTTPException(status_code=403, detail=answer)

router = APIRouter(prefix='/permissions',tags=["Permission"], dependencies=[Depends(require_permission)])


@router.get('/')
async def get_all_permissions():
    answer = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: []
    }
    for p in Permission.select():
        if p.id_role in answer:
            answer[p.id_role].append({'method':p.method, 'url':p.url})
    return answer

@router.get('/{permission_id}/')
async def get_permission_by_id(permission_id: int):
    try:
        permission = Permission.get_by_id(permission_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Разрешение не найдено")

    return {
        "id": permission.id,
        "id_role": permission.id_role,
        "method": permission.method,
        "url": permission.url
    }

@router.get('/{role_id}/')
async def get_permission_by_role(role_id: int):
    answer = []
    for p in Permission.select().where(Permission.id_role == role_id):
        answer.append({'method':p.method, 'url':p.url})
    return answer

@router.post('/{role_id}/')
async def create_permission(role_id: int, method: str, url: str):

    existing = Permission.select().where(
        (Permission.id_role == role_id) &
        (Permission.method == method.upper()) &
        (Permission.url == url)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Такое разрешение уже существует")

    permission = Permission.create(
        id_role=role_id,
        method=method,
        url=url
    )

    return {
        "status_code": 201,
        "detail": "Привилегия создана",
        "id": permission.id
    }

@router.patch('/{id}/')
async def update_permission(id: int, method: str = None, url: str = None):
    try:
        permission = Permission.get_by_id(id)
    except DoesNotExist:
        raise HTTPException(status_code=404,detail='Запись не найдена')
    if method:
        permission.method = method.upper()
    if url:
        permission.url = url

    permission.save()

    return {
        "status_code": 200,
        "detail": "Запись обновлена",
        "id": id
    }

@router.delete('/{id}/')
async def delete_permission(id: int):
    try:
        permission = Permission.get_by_id(id)
    except DoesNotExist:
        raise HTTPException(status_code=404,detail='Запись не найдена')
    permission.delete_instance()
    return {
        "status_code": 200,
        "detail": "Запись удалена",
        "id": id
    }