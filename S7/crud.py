from models import Group
from peewee import * 

def create_group(**data):
    try:
        return Group.create(**data)
    except IntegrityError:
        return None

def delete_group(group_id: int):
    try:
        group = Group.get_by_id(group_id)
    except DoesNotExist:
        return False 
    
    group.is_active = False
    group.save()
    return True

def patch_group(group_id: int, tutor_id: int):
    try:
        group = Group.get_by_id(group_id)
    except DoesNotExist:
        return False
    
    group.tutor_id = tutor_id
    group.save()
    return group, group.name

def info_id(group_id: int):
    try:
        group = Group.get_by_id(group_id)
    except DoesNotExist:
        return False

    return group, group.name

def groups():
    groups = Group.filter(is_active = True)
    if not groups:
        return False
    return [{"id": g.id, "name": g.name} for g in groups]