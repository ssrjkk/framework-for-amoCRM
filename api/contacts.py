"""Contacts API."""

from typing import Optional

import requests

from api.base_api import BaseApi


class ContactsApi(BaseApi):
    """Contacts API for amoCRM."""

    ENDPOINT = "/api/contacts"

    def list(
        self,
        page: int = 1,
        per_page: int = 20,
        query: Optional[str] = None,
    ) -> requests.Response:
        """Get contacts list."""
        return self.get("", page=page, per_page=per_page, query=query)

    def get_by_id(self, contact_id: int) -> requests.Response:
        """Get contact by ID."""
        return self.get(str(contact_id))

    def create(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company_id: Optional[int] = None,
    ) -> requests.Response:
        """Create new contact."""
        data = {"name": name}
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone
        if company_id:
            data["company_id"] = company_id
        return self.post("", **data)

    def update(
        self,
        contact_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> requests.Response:
        """Update contact."""
        data = {}
        if name:
            data["name"] = name
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone
        return self.put(str(contact_id), **data)

    def delete(self, contact_id: int) -> requests.Response:
        """Delete contact."""
        return super().delete(str(contact_id))

    def search(self, query: str) -> requests.Response:
        """Search contacts by name/email/phone."""
        return self.list(query=query)
