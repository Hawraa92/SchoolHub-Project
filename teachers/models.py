from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from datetime import date

class Teacher(models.Model):
    # Basic Personal Information
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    full_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("Full Name")
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date of Birth")
    )
    gender = models.CharField(
        max_length=15,
        choices=[
            ("Male", _("Male")),
            ("Female", _("Female")),
            ("Other", _("Other"))
        ],
        null=True,
        blank=True,
        verbose_name=_("Gender")
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        verbose_name=_("Email")
    )
    mobile = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name=_("Mobile")
    )
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Address")
    )
    # Link to the subjects the teacher is responsible for
    subjects = models.ManyToManyField(
        "students.Subject",
        blank=True,
        verbose_name=_("Subjects Responsible For")
    )

    @property
    def age(self):
        """
        Automatically calculates the teacher's age based on the date of birth.
        """
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def __str__(self):
        return self.full_name or _("Teacher")

    class Meta:
        verbose_name = _("Teacher")
        verbose_name_plural = _("Teachers")
