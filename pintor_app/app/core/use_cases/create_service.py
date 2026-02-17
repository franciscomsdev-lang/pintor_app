from __future__ import annotations

from dataclasses import dataclass

from app.db.repos.services_repo import ServicesRepo


@dataclass(frozen=True, slots=True)
class CreateServiceRequest:
    name: str
    unit: str
    default_unit_price_cents: int


@dataclass(frozen=True, slots=True)
class CreateServiceResponse:
    service_id: str


class CreateServiceUseCase:
    def __init__(self, services_repo: ServicesRepo) -> None:
        self._repo = services_repo

    async def execute(self, req: CreateServiceRequest) -> CreateServiceResponse:
        name = (req.name or "").strip()
        unit = (req.unit or "").strip()

        if not name:
            raise ValueError("Nome do serviço é obrigatório.")
        if not unit:
            raise ValueError("Unidade é obrigatória.")
        if req.default_unit_price_cents < 0:
            raise ValueError("Preço não pode ser negativo.")

        sid = self._repo.create(
            name=name,
            unit=unit,
            default_unit_price_cents=req.default_unit_price_cents,
        )

        return CreateServiceResponse(service_id=sid)
