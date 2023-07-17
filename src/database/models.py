import uuid

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class UUIDMixin(models.Model):

    id = fields.UUIDField(pk=True, default=uuid.uuid4)

    class Meta:
        abstract = True

    class PydanticMeta:
        exclude = ['id']


class Rate(UUIDMixin):
    date = fields.DateField()
    cargo = fields.CharField(max_length=100)
    value = fields.FloatField()

    def __str__(self):
        return self.date

    class Meta:
        table = 'Коэффициент'
        description = 'Модель описывающая коэффициент для расчета стоимости страхования грузов различных типов в' \
                      'зависимости от даты'


RatePydantic = pydantic_model_creator(Rate, name='Rate')
RateInPydantic = pydantic_model_creator(Rate, name='RateIn', exclude_readonly=True)
