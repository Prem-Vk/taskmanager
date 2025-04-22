from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class Task(models.Model):
    class TaskStatus(models.TextChoices):
        STARTED = 'ST', _('Started')
        RUNNING = 'RU', _('Running')
        COMPLETED = 'CO', _('Completed')
        FAILED = 'FA', _('Failed')

    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=2, choices=TaskStatus.choices, default=TaskStatus.STARTED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.task_id}-{self.name}'
