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
        """
        Validate the name field to ensure it is not empty and unique for the user.
        """
        if not value:
            raise serializers.ValidationError("Name field cannot be empty.")
        user_id = self.context.get('user_id')

        if user_id:
            if Task.objects.filter(name=value, user_id=user_id).exists():
                raise serializers.ValidationError("Task with this name already exists.")
        return value


class TaskViewSerializer(BaseTaskSerializer):
    status = serializers.ChoiceField(choices=Task.TaskStatus.choices, source='get_status_display', read_only=True)
    class Meta(BaseTaskSerializer.Meta):
        fields = ['task_id','status',]


class TaskViewInDetailSerializer(BaseTaskSerializer):
    """
    Serializer for viewing task details with display of status labels.
    """
    status = serializers.ChoiceField(choices=Task.TaskStatus.choices, source='get_status_display', read_only=True)


class TaskSerializer(BaseTaskSerializer):

    def validate_status(self, value: str):
        """
        Validate the status field to ensure it is one of the allowed values.
        """
        value = value.strip().lower()

        if value not in [None, '', 'ru', 'cr']:
            raise serializers.ValidationError("Status field can only be 'run' or 'create'/'blank'.")
        return TASK_STATUS_MAP.get(value, Task.TaskStatus.CREATED)


class TaskUpdateSerializer(BaseTaskSerializer):
    def validate_status(self, value: str):
        """
        Validate the status field to ensure it is one of the allowed values.
        """
        value = value.strip().lower()
        if value not in ['ru', 'cr']:
            raise serializers.ValidationError("Status field can only be 'run' or 'create'/.")
        return TASK_STATUS_MAP.get(value, Task.TaskStatus.CREATED)
