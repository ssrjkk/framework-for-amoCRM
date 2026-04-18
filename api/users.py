"""Users API."""

from typing import Optional

import requests

from api.base_api import BaseApi


class UsersApi(BaseApi):
    """Users API for amoCRM."""

    ENDPOINT = "/api/users"

    def list(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> requests.Response:
        """Get users list."""
        return self.get("", page=page, per_page=per_page)

    def get_by_id(self, user_id: int) -> requests.Response:
        """Get user by ID."""
        return self.get(str(user_id))

    def create(
        self,
        name: str,
        email: str,
    ) -> requests.Response:
        """Create new user."""
        return self.post("", name=name, email=email)

    def update(
        self,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> requests.Response:
        """Update user."""
        data = {}
        if name:
            data["name"] = name
        if email:
            data["email"] = email
        return self.put(str(user_id), **data)

    def delete(self, user_id: int) -> requests.Response:
        """Delete user."""
        return super().delete(str(user_id))
