from apiapp.models import Task
from rest_framework import serializers
from apiapp.helpers import TASK_STATUS_MAP


class BaseTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['task_id', 'name', 'status', 'created_at']
        read_only_fields = ['task_id', 'created_at']
        extra_kwargs = {'name': {'required': True},}
        abstract = True

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name field cannot be empty.")

        if Task.objects.filter(name=value).exists():
            raise serializers.ValidationError("Task with this name already exists.")
        return value


class TaskViewSerializer(BaseTaskSerializer):
    status = serializers.ChoiceField(choices=Task.TaskStatus.choices, source='get_status_display', read_only=True)
    class Meta(BaseTaskSerializer.Meta):
        fields = ['task_id','status',]


class TaskViewInDetailSerializer(BaseTaskSerializer):
    status = serializers.ChoiceField(choices=Task.TaskStatus.choices, source='get_status_display', read_only=True)


class TaskSerializer(BaseTaskSerializer):

    def validate_status(self, value: str):
        value = value.strip().lower()

        if value not in [None, '', 'ru', 'cr']:
            raise serializers.ValidationError("Status field can only be 'run' or 'create'/'blank'.")
        return TASK_STATUS_MAP.get(value, Task.TaskStatus.CREATED)


class TaskUpdateSerializer(BaseTaskSerializer):
    def validate_status(self, value: str):
        value = value.strip().lower()
        if value not in ['ru', 'cr']:
            raise serializers.ValidationError("Status field can only be 'run' or 'create'/.")
        return TASK_STATUS_MAP.get(value, Task.TaskStatus.CREATED)
