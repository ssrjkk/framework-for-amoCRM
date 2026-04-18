"""Deals API."""

from typing import Optional

import requests

from api.base_api import BaseApi


class DealsApi(BaseApi):
    """Deals API for amoCRM."""

    ENDPOINT = "/api/deals"

    def list(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
    ) -> requests.Response:
        """Get deals list."""
        return self.get("", page=page, per_page=per_page, status=status)

    def get_by_id(self, deal_id: int) -> requests.Response:
        """Get deal by ID."""
        return self.get(str(deal_id))

    def create(
        self,
        name: str,
        price: float,
        contact_id: Optional[int] = None,
        company_id: Optional[int] = None,
    ) -> requests.Response:
        """Create new deal."""
        data = {"name": name, "price": price}
        if contact_id:
            data["contact_id"] = contact_id
        if company_id:
            data["company_id"] = company_id
        return self.post("", **data)

    def update(
        self,
        deal_id: int,
        name: Optional[str] = None,
        price: Optional[float] = None,
        status: Optional[str] = None,
    ) -> requests.Response:
        """Update deal."""
        data = {}
        if name:
            data["name"] = name
        if price is not None:
            data["price"] = price
        if status:
            data["status"] = status
        return self.put(str(deal_id), **data)

    def delete(self, deal_id: int) -> requests.Response:
        """Delete deal."""
        return super().delete(str(deal_id))

    def update_status(self, deal_id: int, status: str) -> requests.Response:
        """Update deal status."""
        return self.update(deal_id, status=status)
