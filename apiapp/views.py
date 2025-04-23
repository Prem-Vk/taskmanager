from rest_framework import viewsets
from rest_framework.response import Response
from .models import Task
from apiapp.serializers import TaskSerializer, TaskViewSerializer, TaskUpdateSerializer, TaskViewInDetailSerializer
from apiapp.validators import validate_uuid
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from apiapp.tasks import run_task
from apiapp.helpers import validate_updation_status, DEFAULT_TASK_RUNTIME
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes


class TaskViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.all()

    def list(self, request):
        queryset = self.get_queryset().filter(user=request.user).order_by('created_at')
        print(request.user)
        serializer = TaskViewSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if not (pk and validate_uuid(pk)):
            return Response({'error': 'Invalid task ID'}, status=400)
        task = self.get_queryset().filter(task_id=pk, user=request.user).first()
        if task is None:
            return Response(status=404)
        serializer = TaskViewInDetailSerializer(task)
        return Response(serializer.data)

    def _fork_task(self, task_id, user):
        task = self.get_queryset().filter(task_id=task_id, user=user).defer('task_id').first()
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

    def _run_task(self, task: Task, timer: int = DEFAULT_TASK_RUNTIME):
        if task.status == Task.TaskStatus.RUNNING:
            # If the task is running, start the task
            run_task.delay(task.task_id, timer)

    def create(self, request):
        task_id = request.data.pop('fork_task_id', None)
        if task_id and validate_uuid(task_id):
            return self._fork_task(task_id, request.user)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            task.user = request.user
            task.save()
            self._run_task(task, request.data.get('timer', DEFAULT_TASK_RUNTIME))
            return Response({'message': 'Task created successfully'}, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        if not (pk and validate_uuid(pk)):
            return Response({'error': 'Invalid task ID'}, status=400)
        task = self.get_queryset().filter(task_id=pk, user=request.user).first()
        if task is None:
            return Response(status=404)

        if 'status' in request.data:
            if validate_updation_status(request.data['status']) is False:
                return Response({'error': 'Invalid status value'}, status=400)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            task = serializer.save()
            self._run_task(task, request.data.get('timer', DEFAULT_TASK_RUNTIME))
            return Response({'message': 'Task updated successfully'}, status=200)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        task = self.get_queryset().filter(task_id=pk).first()
        if task is None:
            return Response(status=404)
        task.delete()
        return Response({'message': f'Task {pk} deleted successfully'}, status=204)


@api_view(['POST'], )
@authentication_classes([])
@permission_classes([])
def user_signup(request):
    """
    User signup view.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': 'Username, password, and email are required.'}, status=400)

    # Check if user already exists
    user = get_user_model().objects.filter(username=username).first()
    if user:
        return Response({'error': 'User already exists.'}, status=400)

    # Create new user
    user = get_user_model().objects.create(
        username=username,
        email=email,
    )
    user.set_password(password)
    user.save()

    return Response({'message': 'User created successfully.'}, status=201)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def get_jwt_token(request):
    """
    Get JWT token for user.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=400)

    # Authenticate user
    user = get_user_model().objects.filter(username=username).first()
    if not user or not user.check_password(password):
        return Response({'error': 'Invalid credentials.'}, status=401)

    # Generate JWT token
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=200)
