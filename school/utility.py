import os

def image_upload_path(instance, filename):
    instance_id = str(instance.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'school/images/{instance_id}{extension}'

    return file_path

def tor_upload_path(instance, filename):
    instance_id = str(instance.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'school/TOR/{instance_id}{extension}'

    return file_path