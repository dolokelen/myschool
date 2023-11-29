from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .utility import image_upload_path, student_number_generator, tor_upload_path
from .validators import validate_school_year, validate_file_size


class SchoolYear(models.Model):
    year = models.PositiveIntegerField(
        unique=True, validators=[validate_school_year])

    def __str__(self) -> str:
        return str(self.year)


class Department(models.Model):
    """
    It could have a director and a deputy director
    """
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
    FR = 'Freshman'
    SO = 'Sophomore'
    JR = 'Junior'
    SR = 'Senior'
    GR = 'Graduate'
    STATUS_CHOICES = (
        (FR, FR),
        (SO, SO),
        (JR, JR),
        (SR, SR),
        (GR, GR),
    )
    level = models.CharField(max_length=9, choices=STATUS_CHOICES)

    class Meta:
        abstract = True


class Course(Status): 
    """
    Course is created with along with a semester, so preload any 1-m or m-m fields in SemesterSerializer
    """
    departments = models.ManyToManyField(Department, related_name='courses')
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
    """
    It could have a program_overview file field
    """
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
    """
    Could have a caretaker field with FK relationship on Employee
    """
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
    """
    Instead of relying on the id field as the office name, give it a name field.
    """
    building = models.ForeignKey(
        Building, on_delete=models.PROTECT, related_name='offices')
    dimension = models.CharField(max_length=100)


class Document(models.Model):
    """This class is not used in the entire project b/c of limited time."""
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
    # I added this b/c semester was using this class. So delete this field!
    year = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.file_type

    class Meta:
        abstract = True


class Person(models.Model): 
    MALE = 'Male'
    FEMALE = 'Female'
    GENDER_CHOICES = (
        (MALE, MALE),
        (FEMALE, FEMALE)
    )
    CHRISTIAN = 'Christian'
    MUSLIM = 'Muslim'
    NONE = 'None'
    RELIGION_CHOICES = (
        (CHRISTIAN, CHRISTIAN),
        (MUSLIM, MUSLIM),
        (NONE, NONE)
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    religion = models.CharField(max_length=9, choices=RELIGION_CHOICES)
    phone = models.CharField(max_length=15)
    image = models.ImageField(
        upload_to=image_upload_path, validators=[validate_file_size])
    joined_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True


class AbstractStatus(models.Model):
    FULL_TIME = 'Full Time'
    PART_TIME = 'Part Time'
    EMPLOYMENT_STATUS_CHOICES = (
        (FULL_TIME, FULL_TIME),
        (PART_TIME, PART_TIME)
    )
    SINGLE = 'Single'
    MARRIED = 'Married'
    MARITAL_STATUS_CHOICES = (
        (SINGLE, SINGLE),
        (MARRIED, MARRIED)
    )
    HSD = 'High Sch Diploma'
    TRD = 'Trade Sch Certificate'
    BSC = 'Bachelor Degree'
    MSC = 'Master Degree'
    PHD = 'Doctorate Degree'
    HIGHEST_EDUCATION = (
        (HSD, HSD),
        (TRD, TRD),
        (BSC, BSC),
        (MSC, MSC),
        (PHD, PHD)
    )
    marital_status = models.CharField(
        max_length=7, choices=MARITAL_STATUS_CHOICES)
    employment_status = models.CharField(
        max_length=9, choices=EMPLOYMENT_STATUS_CHOICES)
    level_of_education = models.CharField(
        max_length=21, choices=HIGHEST_EDUCATION)

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


class EmployeeAddress(Address):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, primary_key=True, related_name='employeeaddress')


class Teacher(AbstractStatus, Person):
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='teachers')
    supervisor = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='supervisees')
    salary = models.DecimalField(max_digits=6, decimal_places=2)
    office = models.ForeignKey(
        Office, on_delete=models.PROTECT, related_name='teachers')
    term_of_reference = models.FileField(
        upload_to=tor_upload_path, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])


class TeacherAddress(Address):
    teacher = models.OneToOneField(
        Teacher, on_delete=models.CASCADE, primary_key=True, related_name='teacheraddress')


class Major(models.Model):
    name = models.CharField(max_length=150, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='majors')

    def __str__(self) -> str:
        return self.name


class Student(Status, Person):
    """
    Student number is not being correctly populated!
    """
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='students')
    supervisor = models.ForeignKey(
        Teacher, on_delete=models.PROTECT, related_name='mentees')
    major = models.ForeignKey(
        Major, on_delete=models.PROTECT, related_name='students')
    student_number = models.CharField(
        max_length=255, default=student_number_generator)
    registration_fee = models.DecimalField(
        max_digits=6, decimal_places=2)  # Belongs to stemester registration...but it's implementation is not clear yet.
    is_transfer = models.BooleanField(default=False)


class StudentAddress(Address):
    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, primary_key=True, related_name='studentaddress')


class ClassRoom(models.Model):
    building = models.ForeignKey(
        Building, on_delete=models.PROTECT, related_name='classrooms')
    name = models.CharField(max_length=150, unique=True)
    dimension = models.CharField(max_length=150)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class ClassTime(models.Model):
    start_time = models.CharField(max_length=7)
    end_time = models.CharField(max_length=7)
    week_days = models.CharField(max_length=6)

    class Meta:
        unique_together = [['start_time', 'end_time', 'week_days']]

    def __str__(self) -> str:
        return f'{self.start_time} - {self.end_time}, {self.week_days}'


class Section(models.Model):
    name = models.CharField(max_length=2)
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='sections')
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.PROTECT, related_name='sections')
    classtime = models.ForeignKey(
        ClassTime, on_delete=models.PROTECT, related_name='sections')

    class Meta:
        unique_together = [['classroom', 'classtime'], ['name', 'course']]

    def __str__(self) -> str:
        return self.name


class Attendance(models.Model):
    P = 'P'
    A = 'A'
    E = 'E'
    T = 'T'
    MARK_CHOICES = (
        (P, P),
        (A, A),
        (E, E),
        (T, T)
    )
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT)
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, related_name='attendances')
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='attendances')
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT, related_name='attendances')
    mark = models.CharField(max_length=1, choices=MARK_CHOICES)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # They should be date instead of datetime!!!


class Enrollment(models.Model):
    APPROVED = 'Approved'
    PENDING = 'Pending'
    CANCELLED = 'Cancelled'
    STATUS_CHOICES = (
        (PENDING, PENDING),
        (APPROVED, APPROVED),
        (CANCELLED, CANCELLED)
    )
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, related_name='enrollments')
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='enrollments')
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT, related_name='enrollments')
    semester = models.ForeignKey(
        Semester, on_delete=models.PROTECT, related_name='enrollments')
    school_year = models.ForeignKey(
        SchoolYear, on_delete=models.PROTECT, related_name='enrollments')
    status = models.CharField(
        max_length=9, choices=STATUS_CHOICES, default=PENDING)
    has_scholarship = models.BooleanField(default=False)#Remove this field, it bolong to semester registration...but its implementation is not clear yet.
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['student', 'course',
                            'section', 'semester', 'school_year']]


class Teach(models.Model):
    """
    Responsible for assigning sections to teacher
    """
    teacher = models.ForeignKey(
        Teacher, on_delete=models.PROTECT, related_name='teaches')
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='teaches')
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT, related_name='teaches')
    school_year = models.ForeignKey(
        SchoolYear, on_delete=models.PROTECT, related_name='teaches')
    semester = models.ForeignKey(
        Semester, on_delete=models.PROTECT, related_name='teaches')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['teacher', 'course',
                            'section', 'semester', 'school_year']]


class Grade(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, related_name='grades')
    school_year = models.ForeignKey(
        SchoolYear, on_delete=models.PROTECT, related_name='grades')
    semester = models.ForeignKey(
        Semester, on_delete=models.PROTECT, related_name='grades')
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='grades')
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT, related_name='grades')
    attendance = models.DecimalField(max_digits=4, decimal_places=2, validators=[
                                     MinValueValidator(0), MaxValueValidator(10)])
    quiz = models.DecimalField(max_digits=4, decimal_places=2, validators=[
                               MinValueValidator(0), MaxValueValidator(10)])
    assignment = models.DecimalField(max_digits=3, decimal_places=2, validators=[
                                     MinValueValidator(0), MaxValueValidator(5)])
    midterm = models.DecimalField(max_digits=4, decimal_places=2, validators=[
                                  MinValueValidator(0), MaxValueValidator(25)])
    project = models.DecimalField(max_digits=4, decimal_places=2, validators=[
                                  MinValueValidator(0), MaxValueValidator(15)])
    final = models.DecimalField(max_digits=4, decimal_places=2, validators=[
                                MinValueValidator(0), MaxValueValidator(35)])
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['student', 'school_year', 'semester', 'course', 'section']]

# class SemesterEnrollment(models.Model):
#     """
#     This class was not used in this project because of limited time.
#     """
    # semester
    # school_year
    # has_scholarship
    # registration_fee
    # student_status/level
