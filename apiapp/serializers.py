from apiapp.models import Task
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['task_id', 'name', 'status', 'created_at']
        read_only_fields = ['task_id', 'created_at']
        extra_kwargs = {'name': {'required': True},}

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name field cannot be empty.")

        # if Task.objects.filter(name=value).exists():
        #     raise serializers.ValidationError("Task with this name already exists.")
        return value
