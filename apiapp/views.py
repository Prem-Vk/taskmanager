from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Task


class TaskViewSet(viewsets.ViewSet):
    queryset = Task.objects.all()

    def list(self, request):
        pass
    def retrieve(self, request, pk=None):
        pass
    def create(self, request):
        pass
    def update(self, request, pk=None):
        pass
    def destroy(self, request, pk=None):
        pass
    def partial_update(self, request, pk=None):
        pass

