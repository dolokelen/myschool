from django.db import models, transaction
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .validators import validate_school_year, validate_file_size


class SchoolYear(models.Model):
    year = models.PositiveIntegerField(
        unique=True, validators=[validate_school_year])

    def __str__(self) -> str:
        return str(self.year)


class Department(models.Model):
    # director = models.OneToOneField(
    #     'Employee', on_delete=models.SET_NULL, blank=True, null=True, related_name='director')
    # deputy_director = models.OneToOneField(
    #     'Employee', on_delete=models.SET_NULL, blank=True, null=True, related_name='deputydirector')
    name = models.CharField(max_length=200, unique=True)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    duty = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Address(models.Model):
    country = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    community = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self.county}, {self.city}, {self.community} '


class Contact(models.Model):
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.email


class DepartmentAddress(Address):
    department = models.OneToOneField(
        Department, on_delete=models.CASCADE, primary_key=True, related_name='departmentaddress')


class DepartmentContact(Contact):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='departmentcontact')


class Status(models.Model):
    STATUS_CHOICES = (
        ("FR", "Freshman"),
        ("SO", "Sophomore"),
        ("JR", "Junior"),
        ("SR", "Senior"),
        ("GR", "Graduate"),
    )
    level = models.CharField(max_length=2, choices=STATUS_CHOICES)

    class Meta:
        abstract = True


class Course(Status):  # preload any 1-m or m-m fields in SemesterSerializer
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='courses')
    code = models.CharField(max_length=50, unique=True)
    prerequisite = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='prerequisites')
    title = models.CharField(max_length=200, unique=True)
    price_per_credit = models.DecimalField(max_digits=5, decimal_places=2)
    credit = models.PositiveSmallIntegerField()
    additional_fee = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.code


class Semester(models.Model):
    NAME_CHOICES = (
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III')
    )
    name = models.CharField(max_length=3, choices=NAME_CHOICES)
    school_year = models.ForeignKey(
        SchoolYear, on_delete=models.PROTECT, related_name='semesters')
    courses = models.ManyToManyField(Course, related_name='semesters')
    enrollment_start_date = models.DateField()
    enrollment_end_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    # program_overview = models.FileField(upload_to='school/semester', validators=[
    #                                     FileExtensionValidator(allowed_extensions=['pdf'])])

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self._state.adding:
                self.is_current = True

            previous_semesters = Semester.objects.filter(is_current=True)
            previous_semesters.update(is_current=False)

            return super().save(*args, **kwargs)

    class Meta:
        unique_together = [['name', 'school_year']]

    def __str__(self) -> str:
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=200, unique=True)
    # care_taker = models.ForeignKey(
    # 'Employee', on_delete=models.PROTECT, null=True, blank=True, related_name='buildings')
    dimension = models.CharField(max_length=200)
    office_counts = models.PositiveSmallIntegerField()
    toilet_counts = models.PositiveSmallIntegerField()
    classroom_counts = models.PositiveSmallIntegerField()
    date_constructed = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class BuildingAddress(Address):
    building = models.OneToOneField(
        Building, primary_key=True, on_delete=models.CASCADE, related_name='buildingaddress')


class Office(models.Model):
    building = models.ForeignKey(
        Building, on_delete=models.PROTECT, related_name='offices')
    dimension = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f'{self.building} - {self.id}'#This is very terrible in performance, especially at the employee endpoint!!! 
        # return f'{self.id}' #Reduces db query but not readable!


class Document(models.Model):
    FILE_CHOICES = (
        ('SCHOLAR', 'Scholarship'),
        ('ACADEMIC', 'Academic'),
        ('MEDICAL', 'Medical'),
        ('EMP', 'Employeement'),
        ('PROMO', 'Promotion'),
        ('WARNING', 'Warning'),
        ('SUSPEN', 'Suspension'),
        ('JOB', 'Job Related'),
        ('LEAVE', 'Leave'),
    )
    file_type = models.CharField(max_length=8, choices=FILE_CHOICES)
    institution_name = models.CharField(max_length=150)
    file = models.FileField(upload_to='school/documents',
                            validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    date_achieved = models.DateField()
    year = models.DateField(auto_now_add=True)#I added this b/c semester was using this class. So delete this field!

    def __str__(self) -> str:
        return self.file_type

    class Meta:
        abstract = True


class Person(models.Model):#Rename it from pserson to user
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    RELIGION_CHOICES = (
        ('C', 'Christian'),
        ('M', 'Muslim'),
        ('N', 'None')
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    religion = models.CharField(max_length=1, choices=RELIGION_CHOICES)
    image = models.ImageField(upload_to='school/images', validators=[validate_file_size])
    joined_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.user.username


class AbstractStatus(models.Model):
    EMPLOYMENT_STATUS_CHOICES = (
        ('FT', 'Full time'),
        ('PT', 'Part time')
    )
    MARITAL_STATUS_CHOICES = (
        ('S', 'Single'),
        ('M', 'Married')
    )
    marital_status = models.CharField(
        max_length=1, choices=MARITAL_STATUS_CHOICES)
    employment_status = models.CharField(
        max_length=2, choices=EMPLOYMENT_STATUS_CHOICES)

    class Meta:
        abstract = True


class Employee(AbstractStatus, Person):
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='employees')
    supervisor = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisees')
    office = models.ForeignKey(
        Office, on_delete=models.PROTECT, related_name='employees')
    salary = models.DecimalField(max_digits=6, decimal_places=2)
    term_of_reference = models.FileField(
        upload_to='school/TOR', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
