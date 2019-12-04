from django.db import models
from django.contrib.postgres.fields import ArrayField

from django_pewtils.abstract_models import BasicExtendedModel


class TestModel(BasicExtendedModel):

    text_field = models.TextField(null=True)
    foreign_key = models.ForeignKey(
        "testapp.SecondTestModel",
        related_name="foreign_key_reverse",
        null=True,
        on_delete=models.SET_NULL,
    )
    foreign_key_self = models.ForeignKey(
        "testapp.TestModel",
        related_name="foreign_key_self_reverse",
        null=True,
        on_delete=models.SET_NULL,
    )
    one_to_one = models.OneToOneField(
        "testapp.SecondTestModel",
        related_name="one_to_one_reverse",
        null=True,
        on_delete=models.SET_NULL,
    )
    one_to_one_self = models.OneToOneField(
        "testapp.TestModel",
        related_name="one_to_one_self_reverse",
        null=True,
        on_delete=models.SET_NULL,
    )
    many_to_many = models.ManyToManyField(
        "testapp.SecondTestModel", related_name="many_to_many_reverse"
    )
    many_to_many_self = models.ManyToManyField(
        "testapp.TestModel", related_name="many_to_many_self_reverse"
    )
    array_field = ArrayField(models.CharField(max_length=150), default=list)

    def __str__(self):

        string = "{}: {}".format(self._meta.model._meta.model_name.title(), self.pk)

        return string


class SecondTestModel(BasicExtendedModel):

    text_field = models.TextField(null=True)
    foreign_key = models.ForeignKey(
        "testapp.TestModel",
        related_name="foreign_key_reverse",
        null=True,
        on_delete=models.SET_NULL,
    )
    foreign_key_unique = models.ForeignKey(
        "testapp.TestModel",
        related_name="foreign_key_unique_reverse",
        null=True,
        on_delete=models.SET_NULL,
    )
    dummy_field = models.CharField(default="test", max_length=10)

    class Meta:
        unique_together = ("foreign_key_unique", "dummy_field")

    def __str__(self):

        string = "{}: {}".format(self._meta.model._meta.model_name.title(), self.pk)

        return string
