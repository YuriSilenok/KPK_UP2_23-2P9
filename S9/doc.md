# Student Movement Service (Сервис движения студентов)

## Назначение сервиса
Сервис хранит историю движений студентов: отчисление, восстановление, перевод из группы в группу, академические отпуска.

---

## Добавить Movement (запись о движении)

### Параметры запроса

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|-----------------------|
| student_id | ID студента | Обязательно | Integer | строго больше 0 | — |
| movement_type | Тип движения | Обязательно | String | только 'expelled', 'reinstated', 'transferred', 'academic_leave', 'back_from_leave' | — |
| start_date | Дата начала | Обязательно | Date | формат ГГГГ-ММ-ДД | — |
| source_group_id | ID группы источника | Не обязательно | Integer | строго больше 0 | NULL |
| target_group_id | ID группы назначения | Не обязательно | Integer | строго больше 0 | NULL |
| reason | Основание | Не обязательно | String | длина до 255 символов | NULL |
| order_number | Номер приказа | Не обязательно | String | длина до 50 символов | NULL |
| end_date | Дата окончания | Не обязательно | Date | позже start_date (для academic_leave) | NULL |

### Уникальные комбинации параметров
- Для `movement_type = 'transferred'` (перевод): обязательны `source_group_id` и `target_group_id`, причём они не могут быть равны.
- Для `movement_type = 'academic_leave'`: `end_date` должна быть указана и быть позже `start_date`.
- Для `movement_type = 'reinstated'` или `'back_from_leave'`: обязателен `target_group_id`.
- Для `movement_type = 'expelled'`: `source_group_id` обязателен, `target_group_id` не используется.

### Возвращаемые данные (при успешном создании)

| Параметр | Тип |
|----------|-----|
| id | Integer |
| student_id | Integer |
| movement_type | String |
| start_date | Date |
| source_group_id | Integer или NULL |
| target_group_id | Integer или NULL |
| reason | String или NULL |
| order_number | String или NULL |
| end_date | Date или NULL |
| created_at | DateTime |

---

## Изменить Movement по ID

### Параметры запроса

| Параметр | Пояснение | Обязательность | Тип | Ограничение | Значение по умолчанию |
|----------|-----------|----------------|-----|-------------|-----------------------|
| movement_type | Тип движения | Не обязательно | String | только 'expelled', 'reinstated', 'transferred', 'academic_leave', 'back_from_leave' | — |
| start_date | Дата начала | Не обязательно | Date | формат ГГГГ-ММ-ДД | — |
| source_group_id | ID группы источника | Не обязательно | Integer | строго больше 0 | NULL |
| target_group_id | ID группы назначения | Не обязательно | Integer | строго больше 0 | NULL |
| reason | Основание | Не обязательно | String | длина до 255 символов | NULL |
| order_number | Номер приказа | Не обязательно | String | длина до 50 символов | NULL |
| end_date | Дата окончания | Не обязательно | Date | позже start_date | NULL |

### Возвращаемые данные (при успешном изменении)

| Параметр | Тип |
|----------|-----|
| id | Integer |
| student_id | Integer |
| movement_type | String |
| start_date | Date |
| source_group_id | Integer или NULL |
| target_group_id | Integer или NULL |
| reason | String или NULL |
| order_number | String или NULL |
| end_date | Date или NULL |
| updated_at | DateTime |

---

## Удалить Movement по ID

Вернет `True`, если запись о движении была удалена (физическое удаление), иначе вернет `False`.

---

## Получить Movement по ID

### Возвращаемые данные (при успешном поиске)

| Параметр | Пояснение | Тип |
|----------|-----------|-----|
| id | ID записи движения | Integer |
| student_id | ID студента | Integer |
| movement_type | Тип движения | String |
| start_date | Дата начала | Date |
| source_group_id | ID группы источника | Integer или NULL |
| target_group_id | ID группы назначения | Integer или NULL |
| reason | Основание | String или NULL |
| order_number | Номер приказа | String или NULL |
| end_date | Дата окончания | Date или NULL |
| created_at | Дата создания записи | DateTime |

---

## Получить список Movements по заданным параметрам

### Параметры запроса (фильтрация)

| Параметр | Пояснение | Тип | Описание |
|----------|-----------|-----|----------|
| student_id | ID студента | Integer | фильтр по конкретному студенту |
| movement_type | Тип движения | String | фильтр по типу |
| source_group_id | ID группы источника | Integer | фильтр по исходной группе |
| target_group_id | ID группы назначения | Integer | фильтр по целевой группе |
| start_date_from | Начало периода | Date | дата начала движения не ранее |
| start_date_to | Конец периода | Date | дата начала движения не позднее |
| limit | Лимит записей | Integer | максимум 100, по умолчанию 20 |
| offset | Смещение | Integer | для пагинации, по умолчанию 0 |

### Возвращаемые данные (список Movement)

| Параметр | Тип |
|----------|-----|
| id | Integer |
| student_id | Integer |
| movement_type | String |
| start_date | Date |
| source_group_id | Integer или NULL |
| target_group_id | Integer или NULL |
| reason | String или NULL |
| order_number | String или NULL |
| end_date | Date или NULL |

---

## ER-диаграмма

```mermaid
erDiagram
    Student ||--o{ Movement : "имеет"
    Group ||--o{ Movement : "как источник"
    Group ||--o{ Movement : "как назначение"

    Student {
        int id PK
        string full_name
        int group_id FK
        bool is_active
    }

    Group {
        int id PK
        string name
        int year_of_entry
        bool is_active
    }

    Movement {
        int id PK
        int student_id FK
        string movement_type
        date start_date
        int source_group_id FK
        int target_group_id FK
        string reason
        string order_number
        date end_date
        datetime created_at
    }
