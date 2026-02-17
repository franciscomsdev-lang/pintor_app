from __future__ import annotations

from dataclasses import dataclass

from app.db.repos.services_repo import ServicesRepo


@dataclass(frozen=True, slots=True)
class DeleteServiceRequest:
    service_id: str


@dataclass(frozen=True, slots=True)
class DeleteServiceResponse:
    deleted: bool


class DeleteServiceUseCase:
    def __init__(self, services_repo: ServicesRepo) -> None:
        self._repo = services_repo

    async def execute(self, req: DeleteServiceRequest) -> DeleteServiceResponse:
        if not req.service_id:
            raise ValueError("service_id é obrigatório.")

        self._repo.delete(req.service_id)
        return DeleteServiceResponse(deleted=True)
