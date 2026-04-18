import pytest
import json


pytestmark = [pytest.mark.api, pytest.mark.crud]


class TestContactsCRUD:
    def test_list_contacts(self, api_client):
        resp = api_client.contacts.list()
        assert resp.status_code in [200, 401]
        
        if resp.status_code == 200:
            data = resp.json()
            assert "_embedded" in data

    def test_create_contact(self, api_client):
        resp = api_client.contacts.create({
            "name": "API Test Contact"
        })
        assert resp.status_code in [200, 201, 401]

    def test_get_contact_not_found(self, api_client):
        resp = api_client.contacts.get(999999999)
        assert resp.status_code in [404, 401]

    def test_create_and_update_contact(self, api_client):
        create_resp = api_client.contacts.create({
            "name": "Update Test"
        })
        
        if create_resp.status_code != 200:
            pytest.skip("Cannot create contact")
        
        contact_id = create_resp.json()["_embedded"]["contacts"][0]["id"]
        
        update_resp = api_client.contacts.update(contact_id, {
            "name": "Updated Name"
        })
        
        assert update_resp.status_code in [200, 204]
        
        api_client.contacts.delete(contact_id)

    def test_pagination_contacts(self, api_client):
        resp = api_client.contacts.list(page=1, limit=50)
        assert resp.status_code in [200, 401]


class TestCompaniesCRUD:
    def test_list_companies(self, api_client):
        resp = api_client.companies.list()
        assert resp.status_code in [200, 401]

    def test_create_company(self, api_client):
        resp = api_client.companies.create({
            "name": "API Test Company"
        })
        assert resp.status_code in [200, 201, 401]

    def test_update_company(self, api_client):
        create_resp = api_client.companies.create({
            "name": "Test Company"
        })
        
        if create_resp.status_code != 200:
            pytest.skip("Cannot create company")
        
        company_id = create_resp.json()["_embedded"]["companies"][0]["id"]
        
        update_resp = api_client.companies.update(company_id, {
            "name": "Updated Company"
        })
        
        assert update_resp.status_code in [200, 204]
        
        api_client.companies.delete(company_id)


class TestLeadsCRUD:
    def test_list_leads(self, api_client):
        resp = api_client.leads.list()
        assert resp.status_code in [200, 401]

    def test_create_lead(self, api_client):
        resp = api_client.leads.create({
            "name": "Test Lead",
            "price": 50000
        })
        assert resp.status_code in [200, 201, 401]

    def test_get_lead_not_found(self, api_client):
        resp = api_client.leads.get(999999999)
        assert resp.status_code in [404, 401]

    def test_update_lead_status(self, api_client):
        create_resp = api_client.leads.create({
            "name": "Status Test"
        })
        
        if create_resp.status_code != 200:
            pytest.skip("Cannot create lead")
        
        lead_id = create_resp.json()["_embedded"]["leads"][0]["id"]
        
        update_resp = api_client.leads.update(lead_id, {
            "status_id": 142
        })
        
        assert update_resp.status_code in [200, 204]
        
        api_client.leads.delete(lead_id)


class TestTasksCRUD:
    def test_list_tasks(self, api_client):
        resp = api_client.tasks.list()
        assert resp.status_code in [200, 401]

    def test_create_task(self, api_client):
        resp = api_client.tasks.create({
            "name": "Test Task",
            "task_type_id": 1,
            "entity_type": "leads",
            "entity_id": 1
        })
        assert resp.status_code in [200, 201, 401, 422]


class TestPipelines:
    def test_list_pipelines(self, api_client):
        resp = api_client.pipelines.list()
        assert resp.status_code in [200, 401]


class TestUsers:
    def test_list_users(self, api_client):
        resp = api_client.users.list()
        assert resp.status_code in [200, 401]


class TestFields:
    def test_list_contact_fields(self, api_client):
        resp = api_client.fields.list("contacts")
        assert resp.status_code in [200, 401]


class TestTags:
    def test_list_tags(self, api_client):
        resp = api_client.tags.list()
        assert resp.status_code in [200, 401]


class TestWebhooks:
    def test_list_webhooks(self, api_client):
        resp = api_client.webhooks.list()
        assert resp.status_code in [200, 401]