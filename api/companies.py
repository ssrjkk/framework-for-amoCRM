"""Companies API."""

from typing import Optional

import requests

from api.base_api import BaseApi


class CompaniesApi(BaseApi):
    """Companies API for amoCRM."""

    ENDPOINT = "/api/companies"

    def list(
        self,
        page: int = 1,
        per_page: int = 20,
        query: Optional[str] = None,
    ) -> requests.Response:
        """Get companies list."""
        return self.get("", page=page, per_page=per_page, query=query)

    def get_by_id(self, company_id: int) -> requests.Response:
        """Get company by ID."""
        return self.get(str(company_id))

    def create(
        self,
        name: str,
        website: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> requests.Response:
        """Create new company."""
        data = {"name": name}
        if website:
            data["website"] = website
        if phone:
            data["phone"] = phone
        return self.post("", **data)

    def update(
        self,
        company_id: int,
        name: Optional[str] = None,
        website: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> requests.Response:
        """Update company."""
        data = {}
        if name:
            data["name"] = name
        if website:
            data["website"] = website
        if phone:
            data["phone"] = phone
        return self.put(str(company_id), **data)

    def delete(self, company_id: int) -> requests.Response:
        """Delete company."""
        return super().delete(str(company_id))

    def search(self, query: str) -> requests.Response:
        """Search companies by name/website."""
        return self.list(query=query)
