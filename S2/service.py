
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import peewee
from models import Profile, NotificationSettings, db

# ==================== Pydantic схемы ====================

class ProfileCreate(BaseModel):
    full_name: str = Field(..., min_length=1, description="ФИО пользователя")
    telephone: str = Field(..., min_length=10, max_length=10, description="Номер телефона (10 цифр)")
    email: str = Field(..., max_length=254, description="Электронная почта")
    path_to_photo: str = Field(..., min_length=1, description="Путь к фотографии")

    @validator('telephone')
    def validate_telephone(cls, v):
        if not v.isdigit():
            raise ValueError('Номер телефона должен содержать только цифры')
        return v

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Некорректный формат email')
        return v


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, description="ФИО пользователя")
    telephone: Optional[str] = Field(None, min_length=10, max_length=10, description="Номер телефона (10 цифр)")
    email: Optional[str] = Field(None, max_length=254, description="Электронная почта")
    path_to_photo: Optional[str] = Field(None, min_length=1, description="Путь к фотографии")

    @validator('telephone')
    def validate_telephone(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError('Номер телефона должен содержать только цифры')
        return v

    @validator('email')
    def validate_email(cls, v):
        if v is not None and ('@' not in v or '.' not in v):
            raise ValueError('Некорректный формат email')
        return v


class NotificationSettingsCreate(BaseModel):
    parameter: str = Field(..., min_length=1, description="Параметр уведомления")
    value: str = Field(..., min_length=1, description="Значение параметра")


class ProfileResponse(BaseModel):
    id: int
    full_name: str
    telephone: str
    email: str
    path_to_photo: str
    is_active: bool

    class Config:
        orm_mode = True
        from_attributes = True


class NotificationSettingsResponse(BaseModel):
    id: int
    profile_id: int
    parameter: str
    value: str

    class Config:
        orm_mode = True
        from_attributes = True


# ==================== FastAPI приложение ====================

app = FastAPI(
    title="Profile Service API",
    description="API для управления профилями пользователей",
    version="1.0.0"
)


# ==================== Вспомогательные функции ====================

def format_telephone(telephone: str) -> str:
    """Форматирует номер телефона в читаемый вид"""
    if len(telephone) == 10:
        return f"+7({telephone[:3]}){telephone[3:6]}-{telephone[6:8]}-{telephone[8:10]}"
    return telephone


def get_profile_or_404(profile_id: int) -> Profile:
    """Получить профиль по ID или выбросить 404 ошибку"""
    try:
        profile = Profile.get(Profile.id == profile_id)
        return profile
    except peewee.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Профиль с ID {profile_id} не найден")


def profile_to_response(profile: Profile) -> ProfileResponse:
    """Преобразовать объект Profile в ProfileResponse"""
    return ProfileResponse(
        id=profile.id,
        full_name=profile.full_name,
        telephone=format_telephone(profile.telephone),
        email=profile.email,
        path_to_photo=profile.path_to_photo,
        is_active=profile.is_active
    )


def check_telephone_unique(telephone: str, exclude_id: Optional[int] = None):
    """Проверить уникальность телефона"""
    query = Profile.select().where(Profile.telephone == telephone)
    if exclude_id is not None:
        query = query.where(Profile.id != exclude_id)
    if query.exists():
        raise HTTPException(
            status_code=409,
            detail=f"Профиль с телефоном {format_telephone(telephone)} уже существует"
        )


def check_email_unique(email: str, exclude_id: Optional[int] = None):
    """Проверить уникальность email"""
    query = Profile.select().where(Profile.email == email)
    if exclude_id is not None:
        query = query.where(Profile.id != exclude_id)
    if query.exists():
        raise HTTPException(
            status_code=409,
            detail=f"Профиль с email {email} уже существует"
        )


# ==================== Обработчики событий ====================

@app.on_event("startup")
def startup():
    """Подключение к БД при запуске"""
    if db.is_closed():
        db.connect()


@app.on_event("shutdown")
def shutdown():
    """Закрытие соединения с БД при остановке"""
    if not db.is_closed():
        db.close()


# ==================== CRUD операции с профилями ====================

@app.post("/profiles/", response_model=ProfileResponse, status_code=201)
def create_profile(data: ProfileCreate):
    """Создать новый профиль пользователя"""
    check_telephone_unique(data.telephone)
    check_email_unique(data.email)
    
    profile = Profile.create(
        full_name=data.full_name,
        telephone=data.telephone,
        email=data.email,
        path_to_photo=data.path_to_photo,
        is_active=True
    )
    
    return profile_to_response(profile)


@app.put("/profiles/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: int, data: ProfileUpdate):
    """Обновить данные профиля по ID"""
    profile = get_profile_or_404(profile_id)
    
    if data.telephone is not None:
        check_telephone_unique(data.telephone, exclude_id=profile_id)
        profile.telephone = data.telephone
    
    if data.email is not None:
        check_email_unique(data.email, exclude_id=profile_id)
        profile.email = data.email
    
    if data.full_name is not None:
        profile.full_name = data.full_name
    
    if data.path_to_photo is not None:
        profile.path_to_photo = data.path_to_photo
    
    profile.save()
    
    return profile_to_response(profile)


@app.delete("/profiles/{profile_id}")
def delete_profile(profile_id: int):
    """Логически удалить профиль (is_active = False)"""
    profile = get_profile_or_404(profile_id)
    
    profile.is_active = False
    profile.save()
    
    return {"success": True}


@app.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int):
    """Получить профиль по ID"""
    profile = get_profile_or_404(profile_id)
    return profile_to_response(profile)


@app.get("/profiles/", response_model=List[ProfileResponse])
def list_profiles(
    full_name: Optional[str] = Query(None, description="ФИО для фильтрации"),
    telephone: Optional[str] = Query(None, description="Номер телефона для фильтрации"),
    email: Optional[str] = Query(None, description="Email для фильтрации"),
    is_active: Optional[bool] = Query(None, description="Активность профиля")
):
    """Получить список профилей с возможностью фильтрации"""
    query = Profile.select()
    
    if full_name is not None:
        query = query.where(Profile.full_name.contains(full_name))
    
    if telephone is not None:
        query = query.where(Profile.telephone.contains(telephone))
    
    if email is not None:
        query = query.where(Profile.email.contains(email))
    
    if is_active is not None:
        query = query.where(Profile.is_active == is_active)
    
    profiles = list(query)
    return [profile_to_response(profile) for profile in profiles]


# ==================== CRUD операции с настройками уведомлений ====================

@app.post("/profiles/{profile_id}/notifications/", response_model=NotificationSettingsResponse, status_code=201)
def create_notification_settings(profile_id: int, data: NotificationSettingsCreate):
    """Создать настройки уведомлений для профиля"""
    profile = get_profile_or_404(profile_id)
    
    existing = NotificationSettings.select().where(
        (NotificationSettings.profile_id == profile_id) &
        (NotificationSettings.parameter == data.parameter)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Настройка уведомлений с параметром '{data.parameter}' для профиля {profile_id} уже существует"
        )
    
    notification = NotificationSettings.create(
        profile_id=profile_id,
        parameter=data.parameter,
        value=data.value
    )
    
    return NotificationSettingsResponse(
        id=notification.id,
        profile_id=notification.profile_id_id,
        parameter=notification.parameter,
        value=notification.value
    )


@app.put("/profiles/{profile_id}/notifications/", response_model=NotificationSettingsResponse)
def update_notification_settings(profile_id: int, data: NotificationSettingsCreate):
    """Обновить настройки уведомлений для профиля"""
    profile = get_profile_or_404(profile_id)
    
    try:
        notification = NotificationSettings.get(
            (NotificationSettings.profile_id == profile_id) &
            (NotificationSettings.parameter == data.parameter)
        )
    except peewee.DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail=f"Настройка уведомлений с параметром '{data.parameter}' для профиля {profile_id} не найдена"
        )
    
    notification.value = data.value
    notification.save()
    
    return NotificationSettingsResponse(
        id=notification.id,
        profile_id=notification.profile_id_id,
        parameter=notification.parameter,
        value=notification.value
    )


@app.get("/profiles/{profile_id}/notifications/", response_model=List[NotificationSettingsResponse])
def get_notification_settings(profile_id: int):
    """Получить все настройки уведомлений для профиля"""
    profile = get_profile_or_404(profile_id)
    
    notifications = NotificationSettings.select().where(
        NotificationSettings.profile_id == profile_id
    )
    
    return [
        NotificationSettingsResponse(
            id=n.id,
            profile_id=n.profile_id_id,
            parameter=n.parameter,
            value=n.value
        )
        for n in notifications
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
