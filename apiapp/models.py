from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import uuid

class Task(models.Model):
    class TaskStatus(models.TextChoices):
        CREATED = 'cr', _('Created')
        RUNNING = 'ru', _('Running')
        COMPLETED = 'co', _('Completed')
        FAILED = 'fa', _('Failed')

    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=2, choices=TaskStatus.choices, default=TaskStatus.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'user'], name='unique_task_name_per_user')
        ]

    def __str__(self):
        return f'{self.task_id}-{self.name}-{self.status}-{self.user.username if self.user else "No User"}'
