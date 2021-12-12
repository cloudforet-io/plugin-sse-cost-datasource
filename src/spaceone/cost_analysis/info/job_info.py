import functools
from spaceone.api.cost_analysis.plugin import job_pb2
from spaceone.core.pygrpc.message_type import *

__all__ = ['TaskInfo', 'TasksInfo']


def TaskInfo(task_data):
    info = {
        'task_options': change_struct_type(task_data['task_options'])
    }

    return job_pb2.TaskInfo(**info)


def TasksInfo(result, **kwargs):
    tasks_data = result.get('tasks', [])
    last_changed_at = result.get('last_changed_at')

    return job_pb2.TasksInfo(tasks=list(map(functools.partial(TaskInfo, **kwargs), tasks_data)),
                             last_changed_at=last_changed_at)
