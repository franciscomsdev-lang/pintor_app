from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.db.repos.services_repo import ServiceRow


@dataclass(slots=True)
class SettingsVM:
    loading: bool = False
    error: Optional[str] = None

    services: list[ServiceRow] = field(default_factory=list)
    selected_service_id: Optional[str] = None

    # Dialog "Novo serviço"
    dialog_open: bool = False
    new_name: str = ""
    new_unit: str = "M2"  # default
    new_price_text: str = ""  # ex: "120,00" (R$)

    def selected_service(self) -> Optional[ServiceRow]:
        if not self.selected_service_id:
            return None
        for s in self.services:
            if s.id == self.selected_service_id:
                return s
        return None
