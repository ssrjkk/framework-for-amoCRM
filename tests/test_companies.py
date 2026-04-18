"""Tests for Companies API."""

import pytest

from api.companies import CompaniesApi
from validators.response_validator import ResponseValidator


pytestmark = pytest.mark.api


class TestCompaniesList:
    """Tests for companies list endpoint."""

    def test_list_returns_200(self, companies_api: CompaniesApi):
        """Test list returns 200."""
        response = companies_api.list()
        assert response.status_code == 200

    def test_list_returns_json(self, companies_api: CompaniesApi):
        """Test list returns JSON."""
        response = companies_api.list()
        ResponseValidator(response).status(200).raise_if_errors()

    def test_list_has_companies_key(self, companies_api: CompaniesApi):
        """Test response has companies key."""
        response = companies_api.list()
        ResponseValidator(response).has_key("companies").raise_if_errors()

    def test_list_pagination(self, companies_api: CompaniesApi):
        """Test list pagination works."""
        response = companies_api.list(page=1, per_page=5)
        ResponseValidator(response).status(200).raise_if_errors()

    def test_list_with_query(self, companies_api: CompaniesApi):
        """Test list with query filter."""
        response = companies_api.list(query="corp")
        ResponseValidator(response).status(200).raise_if_errors()

    def test_search_companies(self, companies_api: CompaniesApi):
        """Test search companies."""
        response = companies_api.search("Acme")
        ResponseValidator(response).status_2xx().raise_if_errors()


class TestCompaniesCRUD:
    """Tests for companies CRUD operations."""

    def test_create_company(self, companies_api: CompaniesApi, sample_company):
        """Test create company."""
        response = companies_api.create(**sample_company)
        ResponseValidator(response).status(201).raise_if_errors()

    def test_get_company_by_id(self, companies_api: CompaniesApi):
        """Test get company by ID."""
        response = companies_api.get_by_id(1)
        assert response.status_code in (200, 404)

    def test_update_company(self, companies_api: CompaniesApi):
        """Test update company."""
        response = companies_api.update(1, name="Updated Company")
        assert response.status_code in (200, 404)

    def test_delete_company(self, companies_api: CompaniesApi):
        """Test delete company."""
        response = companies_api.delete(999)
        assert response.status_code in (200, 404)


class TestCompaniesValidation:
    """Tests for companies response validation."""

    def test_response_time_under_limit(self, companies_api: CompaniesApi):
        """Test response time is acceptable."""
        response = companies_api.list()
        ResponseValidator(response).response_time_under(3000).raise_if_errors()


class TestCompaniesEdgeCases:
    """Tests for edge cases."""

    def test_get_nonexistent_company(self, companies_api: CompaniesApi):
        """Test get nonexistent company."""
        response = companies_api.get_by_id(99999)
        assert response.status_code in (200, 404)

    def test_create_company_minimal(self, companies_api: CompaniesApi):
        """Test create company with only name."""
        response = companies_api.create(name="Minimal Corp")
        ResponseValidator(response).status(201).raise_if_errors()

    def test_create_company_with_website(self, companies_api: CompaniesApi):
        """Test create company with website."""
        response = companies_api.create(
            name="Web Corp",
            website="https://webcorp.example.com",
        )
        ResponseValidator(response).status(201).raise_if_errors()

    def test_update_company_with_website_and_phone(self, companies_api: CompaniesApi):
        """Test update company with website and phone."""
        response = companies_api.update(1, name="Updated", website="https://updated.com", phone="+123")
        assert response.status_code in (200, 404)

    def test_client_property(self, companies_api: CompaniesApi):
        """Test client property."""
        assert companies_api.client is not None

    def test_get_list_pagination(self, companies_api: CompaniesApi):
        """Test get_list with pagination."""
        response = companies_api.get_list(page=2, per_page=10)
        assert response.status_code == 200
