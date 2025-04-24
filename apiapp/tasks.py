from taskmanager.celery import app
from apiapp.models import Task
import time
import logging


@app.task()
def run_task(task_id, timer):
    """
    For task concurrency, we are using Celery.
    Run a task with a specified timer and update its status to completed.
    """
    task = Task.objects.get(task_id=task_id)
    if task:
        time.sleep(timer)
        task.status = Task.TaskStatus.COMPLETED
        task.save(update_fields=['status'])
    else:
        raise ValueError(f"Issue with task {task_id} not found.")
