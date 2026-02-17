from __future__ import annotations
from dataclasses import dataclass
from app.core.errors import ValidationError
from app.core.ports import QuickQuotesRepositoryPort


@dataclass(frozen=True, slots=True)
class CreateQuickQuoteDraftInput:
    customer_name: str
    materials_included: bool = False


class CreateQuickQuoteDraft:
    def __init__(self, quotes_repo: QuickQuotesRepositoryPort) -> None:
        self.quotes_repo = quotes_repo

    def execute(self, inp: CreateQuickQuoteDraftInput) -> str:
        name = (inp.customer_name or "").strip()
        if not name:
            raise ValidationError("Nome do cliente é obrigatório.")

        quote_id = self.quotes_repo.create_draft(
            customer_name=name,
            materials_included=inp.materials_included,
        )
        return quote_id
