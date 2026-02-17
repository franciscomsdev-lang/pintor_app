from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.db.repos.services_repo import ServiceRow, ServicesRepo


@dataclass(frozen=True, slots=True)
class ListServicesRequest:
    pass


@dataclass(frozen=True, slots=True)
class ListServicesResponse:
    services: Sequence[ServiceRow]


class ListServicesUseCase:
    def __init__(self, services_repo: ServicesRepo) -> None:
        self._repo = services_repo

    async def execute(self, req: ListServicesRequest) -> ListServicesResponse:
        services = self._repo.list_all()
        return ListServicesResponse(services=services)
