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

6. Получение всех настроек уведомлений профиля (GET /profiles/{profile_id}/notifications/)
   - Вход: профиль ID
   - Выход: список настроек
"""

# ============================ Pydantic схемы ============================
class ProfileCreate(BaseModel):
    full_name: str = Field(..., max_length=255)
    telephone: str = Field(..., min_length=10, max_length=10)
    email: EmailStr
    path_to_photo: str = Field(..., max_length=255)

class ProfileResponse(BaseModel):
    id: int
    full_name: str
    telephone: str
    email: EmailStr
    path_to_photo: str
    is_active: bool

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    telephone: Optional[str] = Field(None, min_length=10, max_length=10)
    email: Optional[EmailStr]
    path_to_photo: Optional[str] = Field(None, max_length=255)

class NotificationResponse(BaseModel):
    id: int
    profile: int
    parameter: str
    value: str

# ============================ Вспомогательные функции ============================
def preprocess_phone_number(phone: str) -> str:
    digits = ''.join(filter(str.isdigit, phone))
    digits = digits[-10:]
    return digits

def format_phone_for_display(digits: str) -> str:
    if len(digits) != 10:
        return digits
    area_code = digits[:3]
    first_part = digits[3:6]
    second_part = digits[6:8]
    third_part = digits[8:10]
    return f"+7({area_code}){first_part}-{second_part}-{third_part}"
   
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
    # Проверка уникальности email или телефона
    existing_profile = Profile.select().where((Profile.email == data.email) | (Profile.telephone == preprocess_phone_number(data.telephone))).first()
    if existing_profile:
        raise ValueError("Профиль с таким email или телефоном уже существует.")

    # Создаем профиль
    profile = Profile.create(
        full_name=data.full_name,
        telephone=preprocess_phone_number(data.telephone),
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
        telephone=format_phone_for_display(profile.telephone),
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
        profile.telephone = preprocess_phone_number(data.telephone)
    if data.email is not None:
        profile.email = data.email
    if data.path_to_photo is not None:
        profile.path_to_photo = data.path_to_photo
    # Проверка уникальности email или телефона
    existing_profile = Profile.select().where(profile.email) | (profile.telephone).first()
    if existing_profile:
        raise ValueError("Профиль с таким email или телефоном уже существует.")
    profile.save()

    return ProfileResponse(
        id=profile.id,
        full_name=profile.full_name,
        telephone=format_phone_for_display(profile.telephone),
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
    if is_active:
        query = query.where(Profile.is_active == is_active)

    profiles = list(query)
    return [
        ProfileResponse(
            id=p.id,
            full_name=p.full_name,
            telephone=format_phone_for_display(p.telephone),
            email=p.email,
            path_to_photo=p.path_to_photo,
            is_active=p.is_active
        )
        for p in profiles
    ]


# ---------------- Получить все настройки уведомлений профиля
@app.get("/profiles/{profile_id}/notifications/", response_model=List[NotificationResponse])
def get_notifications(profile_id: int):
    profile = get_profile_or_404(profile_id)
    notifications = NotificationSettings.select().where(NotificationSettings.profile == profile)
    return [
        NotificationResponse(
            id=n.id,
            profile=n.profile_id,
            parameter=n.parameter,
            value=n.value
        )
        for n in notifications
    ]
