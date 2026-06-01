from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from models import db, Subgroup, Student, createTables

# ==================== Pydantic схемы ====================

class SubgroupCreate(BaseModel):
    id_group: int = Field(..., gt=0, description="ID группы")
    subgroup_number: int = Field(..., ge=1, description="Номер подгруппы")


class SubgroupUpdate(BaseModel):
    count_student: int = Field(..., ge=0, description="Количество студентов")


class SubgroupResponse(BaseModel):
    id_subgroup: int
    id_group: int
    subgroup_number: int
    name: str
    is_active: bool
    count_student: int


class MessageResponse(BaseModel):
    message: str


# ==================== FastAPI приложение ====================

app = FastAPI(
    title="Сервис подгрупп",
    description="API для управления подгруппами (вариант №8)",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    createTables()


@app.post("/subgroups", response_model=SubgroupResponse, status_code=201)
def add_subgroup(subgroup_data: SubgroupCreate):
    """Добавить подгруппу"""
    existing = Subgroup.get_or_none(
        (Subgroup.id_group == subgroup_data.id_group) &
        (Subgroup.subgroup_number == subgroup_data.subgroup_number)
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Подгруппа с таким id_group и subgroup_number уже существует"
        )
    
    subgroup = Subgroup(
        id_group=subgroup_data.id_group,
        subgroup_number=subgroup_data.subgroup_number,
        is_active=True
    )
    subgroup.save()
    
    return SubgroupResponse(
        id_subgroup=subgroup.id_subgroup,
        id_group=subgroup.id_group,
        subgroup_number=subgroup.subgroup_number,
        name=subgroup.name,
        is_active=subgroup.is_active,
        count_student=subgroup.count_student
    )


@app.put("/subgroups/{subgroup_id}", response_model=SubgroupResponse)
def update_subgroup(subgroup_id: int, update_data: SubgroupUpdate):
    """Изменить подгруппу по ID (обновить количество студентов)"""
    subgroup = Subgroup.get_or_none(Subgroup.id_subgroup == subgroup_id)
    if subgroup is None:
        raise HTTPException(status_code=404, detail="Подгруппа не найдена")
    
    if not subgroup.is_active:
        raise HTTPException(status_code=400, detail="Нельзя изменить закрытую подгруппу")
    
    current_count = subgroup.count_student
    target_count = update_data.count_student
    
    if target_count > current_count:
        # Добавляем недостающих студентов
        for _ in range(target_count - current_count):
            Student.create(
                id_student=-1,  # Заглушка (реальный ID студента должен поступать из сервиса студентов)
                id_subgroup=subgroup
            )
    elif target_count < current_count:
        # Удаляем лишних студентов
        students_to_remove = list(subgroup.students.limit(current_count - target_count))
        for student in students_to_remove:
            student.delete_instance()
    
    return SubgroupResponse(
        id_subgroup=subgroup.id_subgroup,
        id_group=subgroup.id_group,
        subgroup_number=subgroup.subgroup_number,
        name=subgroup.name,
        is_active=subgroup.is_active,
        count_student=subgroup.count_student
    )


@app.delete("/subgroups/{subgroup_id}", response_model=MessageResponse)
def delete_subgroup(subgroup_id: int):
    """Удалить подгруппу по ID (мягкое удаление)"""
    subgroup = Subgroup.get_or_none(Subgroup.id_subgroup == subgroup_id)
    if subgroup is None:
        raise HTTPException(status_code=404, detail="Подгруппа не найдена")
    
    if not subgroup.is_active:
        return MessageResponse(message="Подгруппа уже закрыта")
    
    subgroup.is_active = False
    subgroup.save()
    return MessageResponse(message="Подгруппа удалена(закрыта)")


@app.get("/subgroups/{subgroup_id}", response_model=SubgroupResponse)
def get_subgroup(subgroup_id: int):
    """Получить подгруппу по ID"""
    subgroup = Subgroup.get_or_none(Subgroup.id_subgroup == subgroup_id)
    if subgroup is None:
        raise HTTPException(status_code=404, detail="Подгруппа не найдена")
    
    return SubgroupResponse(
        id_subgroup=subgroup.id_subgroup,
        id_group=subgroup.id_group,
        subgroup_number=subgroup.subgroup_number,
        name=subgroup.name,
        is_active=subgroup.is_active,
        count_student=subgroup.count_student
    )


@app.get("/subgroups", response_model=List[SubgroupResponse])
def get_subgroups(
    id_group: Optional[int] = Query(None, description="ID группы"),
    subgroup_number: Optional[int] = Query(None, description="Номер подгруппы"),
    name: Optional[str] = Query(None, description="Наименование подгруппы"),
    count_student: Optional[int] = Query(None, description="Количество студентов")
):
    """Получить список подгрупп по заданным параметрам (только активные)"""
    query = Subgroup.select().where(Subgroup.is_active == True)
    
    if id_group is not None:
        query = query.where(Subgroup.id_group == id_group)
    if subgroup_number is not None:
        query = query.where(Subgroup.subgroup_number == subgroup_number)
    
    subgroups = list(query)
    
    if name:
        subgroups = [s for s in subgroups if name.lower() in s.name.lower()]
    
    if count_student is not None:
        subgroups = [s for s in subgroups if s.count_student == count_student]
    
    return [
        SubgroupResponse(
            id_subgroup=s.id_subgroup,
            id_group=s.id_group,
            subgroup_number=s.subgroup_number,
            name=s.name,
            is_active=s.is_active,
            count_student=s.count_student
        )
        for s in subgroups
    ]


# ==================== Дополнительные эндпоинты ====================

@app.post("/subgroups/{subgroup_id}/students/{student_id}")
def add_student_to_subgroup(subgroup_id: int, student_id: int):
    """Добавить конкретного студента в подгруппу"""
    subgroup = Subgroup.get_or_none(Subgroup.id_subgroup == subgroup_id)
    if subgroup is None:
        raise HTTPException(status_code=404, detail="Подгруппа не найдена")
    
    if not subgroup.is_active:
        raise HTTPException(status_code=400, detail="Нельзя добавить студента в закрытую подгруппу")
    
    student, created = Student.get_or_create(
        id_student=student_id,
        defaults={'id_subgroup': subgroup}
    )
    if not created:
        student.id_subgroup = subgroup
        student.save()
    
    return {"message": f"Студент {student_id} добавлен в подгруппу {subgroup_id}"}


@app.delete("/subgroups/{subgroup_id}/students/{student_id}")
def remove_student_from_subgroup(subgroup_id: int, student_id: int):
    """Удалить студента из подгруппы"""
    student = Student.get_or_none(
        (Student.id_student == student_id) &
        (Student.id_subgroup == subgroup_id)
    )
    if student is None:
        raise HTTPException(status_code=404, detail="Студент не найден в подгруппе")
    
    student.id_subgroup = None
    student.save()
    
    return {"message": f"Студент {student_id} удалён из подгруппы {subgroup_id}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
