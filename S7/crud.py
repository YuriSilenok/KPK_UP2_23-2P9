from models import Group
from peewee import * 

def create_group(**data) -> Group:
    return Group.create(**data)

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
    return group

def info_id(group_id: int):
    try:
        group = Group.get_by_id(group_id)
    except DoesNotExist:
        return False

    return group, group.name