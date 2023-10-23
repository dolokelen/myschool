from rest_framework import permissions

class ReadModelPermission(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map = {
        'OPTIONS': [],
        'HEAD': [],
        'GET': ['%(app_label)s.view_%(model_name)s']
    }

class CreateModelPermission(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map = {
        'OPTIONS': [],
        'HEAD': [],
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s']
    }

class UpdateModelPermission(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map = {
        'OPTIONS': [],
        'HEAD': [],
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
    }

class DeleteModelPermission(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map = {
            'OPTIONS': [],
            'HEAD': [],
            'GET': ['%(app_label)s.view_%(model_name)s'],
            'DELETE': ['%(app_label)s.delete_%(model_name)s']
        }


class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET']: ['%(app_label)s.view_%(model_name)s']
        