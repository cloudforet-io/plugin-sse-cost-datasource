from schematics.models import Model
from schematics.types import ListType, StringType
from schematics.types.compound import ModelType

__all__ = ['Tasks']


class TaskOptions(Model):
    billing_year = StringType(required=True)
    billing_month = StringType(required=True)


class Task(Model):
    task_options = ModelType(TaskOptions, required=True)


class Tasks(Model):
    tasks = ListType(ModelType(Task), required=True)
