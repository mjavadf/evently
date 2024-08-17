import pytest
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestCreateevents:
    def test_if_user_is_ananymous_return_401(self):
        client = APIClient()
        response = client.post('/events/', {'name': 'event1'})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED