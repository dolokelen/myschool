import os
from django.db.models import F, Max

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


current_id_number = 0

def _student_id_number_generator():
    global current_id_number
    current_id_number += 1

    return current_id_number  

# def student_number_generator():
#     id = str(_student_id_number_generator())
#     if len(id) < 3:
#         return id.zfill(3)
#     return id

# def student_number_generator():
#     from .models import Student
#     updated_count = Student.objects.filter().update(student_number=F('student_number') + 1)
#     updated_count = str(updated_count)
#     if len(updated_count) < 3:
#         return updated_count.zfill(3)
#     return updated_count


# def student_number_generator():
#     from .models import Student
#     latest_student_number = Student.objects.aggregate(Max('student_number'))['student_number__max']
#     print("LATEST STUDENT NUMBER************", latest_student_number)
#     new_student_number = int(latest_student_number) + 1 if latest_student_number is not None else 1
#     new_student_number = str(new_student_number)
#     print("NEW STUDENT NUMBER*************", new_student_number)
#     if len(new_student_number) < 3:
#         return new_student_number.zfill(3)
#     return new_student_number

def student_number_generator():
    # from .models import Student
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute('SELECT MAX(student_number) FROM school_student')
        latest_student_number = cursor.fetchone()[0]
        print("LATEST STUDENT NUMBER **************", latest_student_number)
    new_student_number = int(latest_student_number) + 1 if latest_student_number is not None else 1
    new_student_number = str(new_student_number)
    print("NEW STUDENT NUMBEER*****************", new_student_number )
    if len(new_student_number) < 3:
        return new_student_number.zfill(3)
    return new_student_number
    #     new_student_number = str(new_student_number).zfill(3)
    # return new_student_number




