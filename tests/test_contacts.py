"""Tests for Contacts API."""

import pytest

from api.contacts import ContactsApi
from validators.response_validator import ResponseValidator


pytestmark = pytest.mark.api


class TestContactsList:
    """Tests for contacts list endpoint."""

    def test_list_returns_200(self, contacts_api: ContactsApi):
        """Test list returns 200."""
        response = contacts_api.list()
        assert response.status_code == 200

    def test_list_returns_json(self, contacts_api: ContactsApi):
        """Test list returns JSON."""
        response = contacts_api.list()
        ResponseValidator(response).status(200).raise_if_errors()

    def test_list_has_contacts_key(self, contacts_api: ContactsApi):
        """Test response has contacts key."""
        response = contacts_api.list()
        ResponseValidator(response).has_key("contacts").raise_if_errors()

    def test_list_pagination(self, contacts_api: ContactsApi):
        """Test list pagination works."""
        response = contacts_api.list(page=1, per_page=5)
        ResponseValidator(response).status(200).raise_if_errors()

    def test_list_with_query(self, contacts_api: ContactsApi):
        """Test list with query filter."""
        response = contacts_api.list(query="test")
        ResponseValidator(response).status(200).raise_if_errors()


class TestContactsCRUD:
    """Tests for contacts CRUD operations."""

    def test_create_contact(self, contacts_api: ContactsApi, sample_contact):
        """Test create contact."""
        response = contacts_api.create(**sample_contact)
        ResponseValidator(response).status(201).raise_if_errors()

    def test_get_contact_by_id(self, contacts_api: ContactsApi):
        """Test get contact by ID."""
        response = contacts_api.get_by_id(1)
        assert response.status_code in (200, 404)

    def test_update_contact(self, contacts_api: ContactsApi):
        """Test update contact."""
        response = contacts_api.update(1, name="Updated Name")
        assert response.status_code in (200, 404)

    def test_delete_contact(self, contacts_api: ContactsApi):
        """Test delete contact."""
        response = contacts_api.delete(999)
        assert response.status_code in (200, 404)

    def test_search_contacts(self, contacts_api: ContactsApi):
        """Test search contacts."""
        response = contacts_api.search("John")
        ResponseValidator(response).status_2xx().raise_if_errors()


class TestContactsValidation:
    """Tests for contacts response validation."""

    def test_response_time_under_limit(self, contacts_api: ContactsApi):
        """Test response time is acceptable."""
        response = contacts_api.list()
        ResponseValidator(response).response_time_under(3000).raise_if_errors()

    def test_valid_json_structure(self, contacts_api: ContactsApi):
        """Test valid JSON structure."""
        response = contacts_api.list()
        validator = ResponseValidator(response)
        validator.status(200)
        assert isinstance(validator.json, dict)


class TestContactsEdgeCases:
    """Tests for edge cases."""

    def test_list_nonexistent_page(self, contacts_api: ContactsApi):
        """Test list with large page number."""
        response = contacts_api.list(page=9999)
        assert response.status_code == 200

    def test_get_nonexistent_contact(self, contacts_api: ContactsApi):
        """Test get nonexistent contact."""
        response = contacts_api.get_by_id(99999)
        assert response.status_code in (200, 404)

    def test_create_contact_minimal_data(self, contacts_api: ContactsApi):
        """Test create contact with only name."""
        response = contacts_api.create(name="Minimal Contact")
        ResponseValidator(response).status(201).raise_if_errors()

    def test_create_contact_with_all_fields(self, contacts_api: ContactsApi, sample_contact):
        """Test create contact with all fields."""
        response = contacts_api.create(**sample_contact)
        ResponseValidator(response).status(201).raise_if_errors()

    def test_update_contact_with_all_fields(self, contacts_api: ContactsApi):
        """Test update contact with all fields."""
        response = contacts_api.update(1, name="Updated", email="updated@test.com", phone="+123")
        assert response.status_code in (200, 404)

    def test_create_contact_with_company_id(self, contacts_api: ContactsApi):
        """Test create contact with company_id."""
        response = contacts_api.create(name="With Company", company_id=1)
        ResponseValidator(response).status(201).raise_if_errors()
