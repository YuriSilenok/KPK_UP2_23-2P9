import requests
import json

BASE_URL = "http://localhost:8000"


def print_response(response):
    print(f"Статус: {response.status_code}")
    if response.text:
        try:
            print(f"Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Ответ: {response.text}")
    print("-" * 50)


def add_subgroup(id_group: int, subgroup_number: int):
    print(f"\n→ Создание подгруппы: id_group={id_group}, subgroup_number={subgroup_number}")
    response = requests.post(
        f"{BASE_URL}/subgroups",
        json={"id_group": id_group, "subgroup_number": subgroup_number}
    )
    print_response(response)
    return response.json().get("id_subgroup") if response.status_code == 201 else None


def get_subgroup(subgroup_id: int):
    print(f"\n→ Получение подгруппы ID={subgroup_id}")
    response = requests.get(f"{BASE_URL}/subgroups/{subgroup_id}")
    print_response(response)
    return response.json() if response.status_code == 200 else None


def update_subgroup(subgroup_id: int, id_group: int = None, subgroup_number: int = None):
    print(f"\n→ Обновление подгруппы ID={subgroup_id}: id_group={id_group}, subgroup_number={subgroup_number}")
    data = {}
    if id_group is not None:
        data["id_group"] = id_group
    if subgroup_number is not None:
        data["subgroup_number"] = subgroup_number
    response = requests.put(f"{BASE_URL}/subgroups/{subgroup_id}", json=data)
    print_response(response)
    return response.json() if response.status_code == 200 else None


def delete_subgroup(subgroup_id: int):
    print(f"\n→ Удаление подгруппы ID={subgroup_id}")
    response = requests.delete(f"{BASE_URL}/subgroups/{subgroup_id}")
    print(f"Статус: {response.status_code}")
    print(f"Ответ (bool): {response.text}")
    print("-" * 50)
    return response.status_code == 200 and response.text == "true"


def get_all_subgroups(params: dict = None):
    print(f"\n→ Получение списка подгрупп с фильтрами: {params}")
    response = requests.get(f"{BASE_URL}/subgroups", params=params or {})
    print_response(response)
    return response.json() if response.status_code == 200 else []


def main():
    print("=" * 50)
    print("Клиент сервиса подгрупп (вариант №8)")
    print("=" * 50)
    
    # 1. Создание подгрупп
    sg1 = add_subgroup(1, 1)
    sg2 = add_subgroup(1, 2)
    sg3 = add_subgroup(2, 1)
    
    # 2. Получение по ID
    if sg1:
        get_subgroup(sg1)
    
    # 3. Обновление (меняем id_group и subgroup_number)
    if sg1:
        update_subgroup(sg1, id_group=3, subgroup_number=5)
    
    # 4. Получение списка с фильтрами
    get_all_subgroups()
    get_all_subgroups({"id_group": 3})
    get_all_subgroups({"subgroup_number": 5})
    get_all_subgroups({"name": "3-5"})
    
    # 5. Удаление
    if sg1:
        delete_subgroup(sg1)
    
    # 6. Проверка после удаления
    print("\n→ Проверка после удаления (только активные)")
    get_all_subgroups()


if __name__ == "__main__":
    main()
