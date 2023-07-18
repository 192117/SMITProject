import uuid

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class UUIDMixin(models.Model):
    """An abstract base model class that adds UUID and created fields to models."""

    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    created = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True

    class PydanticMeta:
        exclude = ['id', 'created']


class Rate(UUIDMixin):
    """A model describing coefficients for calculating insurance costs for various cargo types based on the date."""
    date = fields.DateField()
    cargo = fields.CharField(max_length=100)
    value = fields.FloatField()

    def __str__(self):
        return self.date

    class Meta:
        table = 'Коэффициент'
        description = 'Модель описывающая коэффициент для расчета стоимости страхования грузов различных типов в' \
                      'зависимости от даты'
        unique_together = ('date', 'cargo')


RatePydantic = pydantic_model_creator(Rate, name='Rate')
RateInPydantic = pydantic_model_creator(Rate, name='RateIn', exclude_readonly=True)
