from django.db import models
from .validators import validate_school_year


class SchoolYear(models.Model):
    year = models.PositiveIntegerField(
        primary_key=True, validators=[validate_school_year])

    def __str__(self) -> str:
        return str(self.year)
