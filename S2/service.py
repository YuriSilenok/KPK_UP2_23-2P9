from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from peewee import *
from models import Profile, NotificationSettings

app = FastAPI(title="Profiles API", description="API для управления пользователями и их настройками", version="1.0.0")

# ============================ Документация API ============================
"""
API включает следующие эндпоинты:

1. Создание профиля (POST /profiles/)
   - Вход: JSON с полями full_name, telephone, email, path_to_photo
   - Выход: созданный профиль с ID

2. Получение профиля по ID (GET /profiles/{profile_id})
   - Вход: ID профиля
   - Выход: профиль

3. Обновление профиля (PUT /profiles/{profile_id})
   - Вход: ID профиля + JSON с изменяемыми полями
   - Выход: обновленный профиль

4. Мягкое удаление профиля (DELETE /profiles/{profile_id})
   - Вход: ID
   - Выход: success True/False

5. Получение списка профилей (GET /profiles/)
   - Вход: фильтры через query параметры
   - Выход: список профилей

6. Создание настройки уведомлений (POST /profiles/{profile_id}/notifications/)
   - Вход: JSON parameter, value
   - Выход: созданная настройка

7. Обновление настройки уведомлений (PUT /profiles/{profile_id}/notifications/)
   - Вход: JSON parameter, value
   - Выход: обновленная настройка

8. Получение всех настроек уведомлений профиля (GET /profiles/{profile_id}/notifications/)
   - Вход: профиль ID
   - Выход: список настроек
"""

# ============================ Pydantic схемы ============================
class ProfileCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    telephone: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    path_to_photo: str = Field(..., min_length=1, max_length=255)

class ProfileResponse(BaseModel):
    id: int
    full_name: str
    telephone: str
    email: EmailStr
    path_to_photo: str
    is_active: bool

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    telephone: Optional[str] = Field(None, min_length=5, max_length=20)
    email: Optional[EmailStr]
    path_to_photo: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool]

class NotificationCreate(BaseModel):
    parameter: str = Field(..., description="имя параметра")
    value: str = Field(..., description="значение параметра")

class NotificationUpdate(BaseModel):
    parameter: str
    value: str

class NotificationResponse(BaseModel):
    id: int
    profile: int
    parameter: str
    value: str

# ============================ Вспомогательные функции ============================
def format_telephone(telephone: str) -> str:
    # Можно дополнительно реализовать форматирование телефонного номера
    return telephone

def get_profile_or_404(profile_id: int) -> Profile:
    try:
        profile = Profile.get_by_id(profile_id)
        if not profile.is_active:
            raise HTTPException(status_code=404, detail="Профиль не активен")
        return profile
    except Profile.DoesNotExist:
        raise HTTPException(status_code=404, detail="Профиль не найден")

# ============================ API эндпоинты ============================

# ---------------- Создание профиля
@app.post("/profiles/", response_model=ProfileResponse)
def create_profile(data: ProfileCreate):
    # Проверка на уникальность email или телефон (если нужно)
    # Создаем профиль
    profile = Profile.create(
        full_name=data.full_name,
        telephone=format_telephone(data.telephone),
        email=data.email,
        path_to_photo=data.path_to_photo,
        is_active=True
    )
    return ProfileResponse(
        id=profile.id,
        full_name=profile.full_name,
        telephone=profile.telephone,
        email=profile.email,
        path_to_photo=profile.path_to_photo,
        is_active=profile.is_active
    )

# ---------------- Получить профиль по ID
@app.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int):
    profile = get_profile_or_404(profile_id)
    return ProfileResponse(
        id=profile.id,
        full_name=profile.full_name,
        telephone=profile.telephone,
        email=profile.email,
        path_to_photo=profile.path_to_photo,
        is_active=profile.is_active
    )

# ---------------- Обновить профиль
@app.put("/profiles/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: int, data: ProfileUpdate):
    profile = get_profile_or_404(profile_id)

    if data.full_name is not None:
        profile.full_name = data.full_name
    if data.telephone is not None:
        profile.telephone = format_telephone(data.telephone)
    if data.email is not None:
        profile.email = data.email
    if data.path_to_photo is not None:
        profile.path_to_photo = data.path_to_photo
    if data.is_active is not None:
        profile.is_active = data.is_active

    profile.save()

    return ProfileResponse(
        id=profile.id,
        full_name=profile.full_name,
        telephone=profile.telephone,
        email=profile.email,
        path_to_photo=profile.path_to_photo,
        is_active=profile.is_active
    )

# ---------------- Мягкое удаление профиля
@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: int):
    profile = get_profile_or_404(profile_id)
    # логика 'удаления'
    profile.is_active = False
    profile.save()
    return {"success": True}

# ---------------- Получение списка профилей
@app.get("/profiles/", response_model=List[ProfileResponse])
def list_profiles(
    full_name: Optional[str] = Query(None),
    telephone: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True)
):
    query = Profile.select()
    if full_name:
        query = query.where(Profile.full_name.contains(full_name))
    if telephone:
        query = query.where(Profile.telephone.contains(telephone))
    if email:
        query = query.where(Profile.email.contains(email))
    if is_active is not None:
        query = query.where(Profile.is_active == is_active)

    profiles = list(query)
    return [
        ProfileResponse(
            id=p.id,
            full_name=p.full_name,
            telephone=p.telephone,
            email=p.email,
            path_to_photo=p.path_to_photo,
            is_active=p.is_active
        )
        for p in profiles
    ]

# ---------------- Создание настройки уведомлений
@app.post("/profiles/{profile_id}/notifications/", response_model=NotificationResponse)
def create_notification(profile_id: int, data: NotificationCreate):
    profile = get_profile_or_404(profile_id)
    # проверка уникальности параметра у данного профиля
    existing = NotificationSettings.select().where(
        (NotificationSettings.profile == profile) &
        (NotificationSettings.parameter == data.parameter)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Параметр уже существует")
    notification = NotificationSettings.create(
        profile=profile,
        parameter=data.parameter,
        value=data.value
    )
    return NotificationResponse(
        id=notification.id,
        profile=profile.id,
        parameter=notification.parameter,
        value=notification.value
    )

# ---------------- Обновление настройки уведомлений
@app.put("/profiles/{profile_id}/notifications/", response_model=NotificationResponse)
def update_notification(profile_id: int, data: NotificationUpdate):
    profile = get_profile_or_404(profile_id)
    notification = NotificationSettings.select().where(
        (NotificationSettings.profile == profile) &
        (NotificationSettings.parameter == data.parameter)
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Настройка не найдена")
    notification.value = data.value
    notification.save()
    return NotificationResponse(
        id=notification.id,
        profile=profile.id,
        parameter=notification.parameter,
        value=notification.value
    )

# ---------------- Получить все настройки уведомлений профиля
@app.get("/profiles/{profile_id}/notifications/", response_model=List[NotificationResponse])
def get_notifications(profile_id: int):
    profile = get_profile_or_404(profile_id)
    notifications = NotificationSettings.select().where(NotificationSettings.profile == profile)
    return [
        NotificationResponse(
            id=n.id,
            profile=profile.id,
            parameter=n.parameter,
            value=n.value
        )
        for n in notifications
    ]
