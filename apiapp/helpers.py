from apiapp.models import Task
from decouple import config

TASK_STATUS_MAP = {
    # For creating and running tasks
    'cr': Task.TaskStatus.CREATED,
    'ru': Task.TaskStatus.RUNNING,
    'co': Task.TaskStatus.COMPLETED,
    'fa': Task.TaskStatus.FAILED,
    '': Task.TaskStatus.CREATED,
}

DEFAULT_TASK_RUNTIME = config('DEFAULT_TASK_RUNTIME', default=1, cast=int)

def validate_updation_status(status: str) -> bool:
    if status.strip().lower() not in ['ru', 'fa', 'co']:
        return False
    return True
