from rest_framework import viewsets
from rest_framework.response import Response
from .models import Task
from apiapp.serializers import TaskSerializer
from rest_framework.decorators import action
from apiapp.validators import validate_uuid

from django.core.validators import RegexValidator

class TaskViewSet(viewsets.ViewSet):

    def get_queryset(self):
        return Task.objects.all()

    def list(self, request):
        queryset = self.get_queryset().order_by('created_at')
        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        task = self.queryset.filter(task_id=pk).first()
        if task is None:
            return Response(status=404)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def _fork_task(self, task_id):
        task = self.get_queryset().filter(task_id=task_id).defer('task_id').first()
        if task is None:
            return Response({'error': f'Task with id:-{task_id} not found'}, status=404)
        # If task exists, create a new task with the same name
        new_task = TaskSerializer(data={'name': f'{task.name}-forked',})
        if new_task.is_valid():
            new_task_instance = new_task.save()
            # Return the new task details
            serializer = TaskSerializer(new_task_instance)
            return Response(serializer.data)
        return Response(new_task.errors, status=400)

    def create(self, request):
        task_id = request.data.pop('task_id', None)

        if task_id and validate_uuid(task_id):
            return self._fork_task(task_id)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            return Response(TaskSerializer(task).data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        task = self.queryset.filter(task_id=pk).first()
        if task is None:
            return Response(status=404)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            task = serializer.save()
            return Response(TaskSerializer(task).data, status=200)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        task = self.queryset.filter(task_id=pk).first()
        if task is None:
            return Response(status=404)
        task.delete()
        return Response({'message': f'Task {pk} deleted successfully'}, status=204)
