from django.core.exceptions import ValidationError


def validate_school_year(value):
    if len(str(value)) != 4:
        raise ValidationError('Year must be four digits.')
    
def validate_file_size(file):
    max_size_in_kb = 300
    if file.size > max_size_in_kb * 1024:
        raise ValidationError(f'File size cannot be larger than {max_size_in_kb}KB')