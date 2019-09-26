from django.db import models

from django_pewtils.abstract_models import BasicExtendedModel


class TestModel(BasicExtendedModel):

    text_field = models.TextField()
    second_related_object = models.ForeignKey(
        "testapp.SecondTestModel",
        related_name="first_related_object",
        on_delete=models.CASCADE,
    )


class SecondTestModel(BasicExtendedModel):

    text_field = models.TextField(null=True)
