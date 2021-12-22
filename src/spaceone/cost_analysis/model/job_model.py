from schematics.models import Model
from schematics.types import ListType, IntType, DateTimeType
from schematics.types.compound import ModelType

__all__ = ['Tasks']


class TaskOptions(Model):
    billing_year = IntType(required=True)
    billing_month = IntType(required=True)


class Task(Model):
    task_options = ModelType(TaskOptions, required=True)


class Changed(Model):
    start = DateTimeType(required=True)
    end = DateTimeType(default=None)


class Tasks(Model):
    tasks = ListType(ModelType(Task), required=True)
    changed = ListType(ModelType(Changed), default=[])
