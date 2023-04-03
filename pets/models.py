from django.db import models


class PetSex(models.TextChoices):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Not Informed"


class Pet(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    weight = models.FloatField()
    sex = models.CharField(max_length=20, choices=PetSex.choices, default=PetSex.OTHER)

    group = models.ForeignKey(
        "groups.Group", on_delete=models.PROTECT, related_name="pets"
    )
