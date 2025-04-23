from taskmanager.celery import app
from apiapp.models import Task
import time
import logging


@app.task()
def run_task(task_id, timer):
    task = Task.objects.get(task_id=task_id)
    logging.error("Task ID:", task_id, task, task.status)
    if task:
        time.sleep(timer)
        task.status = Task.TaskStatus.COMPLETED
        task.save(update_fields=['status'])
    else:
        raise ValueError(f"Issue with task {task_id} not found.")
