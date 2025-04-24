from rest_framework.test import APITestCase
from django.urls import reverse
from apiapp.models import Task
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from unittest.mock import patch
from apiapp.tasks import run_task
import uuid


class TaskModelTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.client = APIClient()
        cls.access_token = cls.client.post(
            reverse('token_obtain_pair'),
            data={'username': 'testuser', 'password': 'testpass'},
            format='json'
        )

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token.data['access']}")

    def test_task_creation(self):
        """
        Test task creation.
        """
        response = self.client.post(
            reverse('task-list'),
            data={
                'name': 'Test Task',
                'status': 'cr',
            },
        )
        task = Task.objects.filter(name='Test Task', user=self.user)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(task.count(), 1)
        self.assertEqual(task[0].name, 'Test Task')
        self.assertEqual(task[0].status, 'cr')

    def test_running_task_creation(self):
        """
        Test task creation with status 'ru'.
        The test will check if the task is created with status 'ru' and if the run_task function is called.
        Once the task is created, it will simulate running the task and check if the status changes to 'co'.
        """
        with patch('apiapp.tasks.run_task.delay') as mock_run_task:
            response = self.client.post(
                reverse('task-list'),
                data={
                    'name': 'Running Task',
                    'status': 'ru',
                    'timer': 1,
                },
            )
            task = Task.objects.get(name='Running Task', user=self.user)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(Task.objects.filter(name='Running Task', user=self.user).count(), 1)
            self.assertEqual(task.name, 'Running Task')
            self.assertEqual(task.status, 'ru')
            mock_run_task.assert_called_once_with(task.task_id, 1)

            run_task(task.task_id, 0)
            task.refresh_from_db()
            self.assertEqual(task.status, 'co')

    def test_task_creation_with_invalid_status(self):
        """
        Test task creation with invalid status.
        """
        response = self.client.post(
            reverse('task-list'),
            data={
                'name': 'Invalid Task',
                'status': 'invalid-status',
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'][0].title(), '"Invalid-Status" Is Not A Valid Choice.')

    def test_get_task_list(self):
        """
        Test task list retrieval.
        """
        response = self.client.get(reverse('task-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Task.objects.filter(user=self.user).count())

    def test_get_task_detail(self):
        """
        Test task detail retrieval.
        As we are using different serializers for list and detail views,
        we are getting task status as Created (labelname) instead of cr (value).
        """
        task = Task.objects.create(name='Test Task', status='cr', user=self.user)
        response = self.client.get(reverse('task-detail', args=[task.task_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test Task')
        self.assertEqual(response.data['status'], 'Created')
        self.assertEqual(response.data['task_id'], str(task.task_id))

    def test_task_detail_with_invalid_id(self):
        """
        Test task detail retrieval with invalid task ID.
        """
        response = self.client.get(reverse('task-detail', args=['invalid-id']))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid task ID')

    def test_get_task_list_with_status_filter(self):
        """
        Test task list retrieval with status filter.
        """
        Task.objects.create(name='Test Task 1', status='co', user=self.user)
        Task.objects.create(name='Test Task 2', status='cr', user=self.user)
        response = self.client.get(reverse('task-list'), {'status': 'cr'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), Task.objects.filter(status='cr', user=self.user).count())

    def test_update_task(self):
        """
        Test task update.
        To change task name as well as status (running). Which will call run_task function.
        To complete the task.
        """
        with patch('apiapp.tasks.run_task.delay') as mock_run_task:
            task = Task.objects.create(name='Test Task 96', status='cr', user=self.user)
            response = self.client.put(
                reverse('task-detail', args=[task.task_id]),
                data={
                    'name': 'Updated Task 24',
                    'status': 'ru',
                    'timer': 1,
                },
            )
            task.refresh_from_db()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(task.name, 'Updated Task 24')
            self.assertEqual(task.status, 'ru')
            mock_run_task.assert_called_once_with(task.task_id, 1)

            run_task(task.task_id, 0)
            task.refresh_from_db()
            self.assertEqual(task.status, 'co')

    def test_update_task_with_invalid_id(self):
        """
        Test task update with invalid task ID.
        """
        response = self.client.put(reverse('task-detail', args=['invalid-id']), data={'name': 'Updated Task'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid task ID')

    def test_update_task_with_nonexistent_id(self):
        """
        Test task update with nonexistent task ID.
        """
        invalid_task_id = str(uuid.uuid4())
        response = self.client.put(reverse('task-detail', args=[invalid_task_id]), data={'name': 'Updated Task'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], f'Task with id:-{invalid_task_id} not found')

    def test_update_task_with_invalid_status(self):
        """
        Test task update with invalid status.
        """
        task = Task.objects.create(name='Test Task 97', status='cr', user=self.user)
        response = self.client.put(
            reverse('task-detail', args=[task.task_id]),
            data={
                'name': 'Updated Task 25',
                'status': 'invalid-status',
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid status value')

    def test_delete_task(self):
        """
        Test task deletion.
        """
        task = Task.objects.create(name='Test Task 98', status='cr', user=self.user)
        response = self.client.delete(reverse('task-detail', args=[task.task_id]))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Task.objects.filter(task_id=task.task_id).count(), 0)
        self.assertEqual(response.data['message'], f'Task {task.task_id} deleted successfully')

    def test_delete_task_with_invalid_id(self):
        """
        Test task deletion with invalid task ID.
        """
        response = self.client.delete(reverse('task-detail', args=['invalid-id']))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid task ID')

    def test_task_unique_name_per_user(self):
        """
        Test task unique name constraint & validation per user.
        """
        self.user_2 = User.objects.create_user(username='testuser2', password='testpass2')
        self.client_2 = APIClient()
        self.access_token_2 = self.client_2.post(
            reverse('token_obtain_pair'),
            data={'username': 'testuser2', 'password': 'testpass2'},
            format='json'
        )
        self.client_2.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_2.data['access']}")
        response = self.client.post(
            reverse('task-list'),
            data={
                'name': 'Test Task 20',
                'status': 'cr',
            },
        )
        self.assertEqual(response.status_code, 201)
        task_1 = Task.objects.get(name='Test Task 20', user=self.user)

        response_2 = self.client_2.post(
            reverse('task-list'),
            data={
                'name': 'Test Task 20',
                'status': 'cr',
            },
        )
        task_2 = Task.objects.get(name='Test Task 20', user=self.user_2)
        self.assertEqual(response_2.status_code, 201)
        self.assertNotEqual(task_1.user, task_2.user)

        response_3 = self.client_2.post(
            reverse('task-list'),
            data={
                'name': 'Test Task 20',
                'status': 'cr',
            },
        )

        self.assertEqual(response_3.status_code, 400)
        self.assertEqual(response_3.data['name'][0].title(), 'Task With This Name Already Exists.')

        # Check for get-task-list for user_2
        response_4 = self.client_2.get(reverse('task-list'))
        self.assertEqual(response_4.status_code, 200)
        self.assertEqual(len(response_4.data), Task.objects.filter(user=self.user_2).count())
