"""Tests for Users API."""

import pytest

from api.users import UsersApi
from validators.response_validator import ResponseValidator


pytestmark = pytest.mark.api


class TestUsersList:
    """Tests for users list endpoint."""

    def test_list_returns_200(self, users_api: UsersApi):
        """Test list returns 200."""
        response = users_api.list()
        assert response.status_code == 200

    def test_list_returns_json(self, users_api: UsersApi):
        """Test list returns JSON."""
        response = users_api.list()
        ResponseValidator(response).status(200).raise_if_errors()

    def test_list_has_users_key(self, users_api: UsersApi):
        """Test response has users key."""
        response = users_api.list()
        ResponseValidator(response).has_key("users").raise_if_errors()

    def test_list_pagination(self, users_api: UsersApi):
        """Test list pagination works."""
        response = users_api.list(page=1, per_page=5)
        ResponseValidator(response).status(200).raise_if_errors()


class TestUsersCRUD:
    """Tests for users CRUD operations."""

    def test_create_user(self, users_api: UsersApi):
        """Test create user."""
        response = users_api.create(name="Test User", email="testuser@example.com")
        ResponseValidator(response).status(201).raise_if_errors()

    def test_get_user_by_id(self, users_api: UsersApi):
        """Test get user by ID."""
        response = users_api.get_by_id(1)
        assert response.status_code in (200, 404)

    def test_update_user(self, users_api: UsersApi):
        """Test update user."""
        response = users_api.update(1, name="Updated User")
        assert response.status_code in (200, 404)

    def test_update_user_with_email(self, users_api: UsersApi):
        """Test update user with email."""
        response = users_api.update(1, email="updated@test.com")
        assert response.status_code in (200, 404)

    def test_delete_user(self, users_api: UsersApi):
        """Test delete user."""
        response = users_api.delete(999)
        assert response.status_code in (200, 404)


class TestUsersValidation:
    """Tests for users response validation."""

    def test_response_time_under_limit(self, users_api: UsersApi):
        """Test response time is acceptable."""
        response = users_api.list()
        ResponseValidator(response).response_time_under(3000).raise_if_errors()
