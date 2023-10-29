from django.db import models, transaction
from .validators import validate_school_year


class SchoolYear(models.Model):
    year = models.PositiveIntegerField(
        unique=True, validators=[validate_school_year])

    def __str__(self) -> str:
        return str(self.year)


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    duty = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class DepartmentAddress(models.Model):
    department = models.OneToOneField(
        Department, on_delete=models.CASCADE, primary_key=True)
    country = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    community = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.county}, {self.city}, {self.community} '


class DepartmentContact(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self) -> str:
        return self.email


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
