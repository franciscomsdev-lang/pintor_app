from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.core.config import load_config
from app.db.database import connect_sqlite

from app.db.repos.services_repo import ServicesRepo
from app.db.repos.quick_quotes_repo import QuickQuotesRepo

from app.core.use_cases.create_quick_quote_draft import CreateQuickQuoteDraft
from app.core.use_cases.add_item_to_quote import AddItemToQuote
from app.core.use_cases.get_quote_details import GetQuoteDetails

# NOVOS USE CASES
from app.core.use_cases.list_services import ListServicesUseCase
from app.core.use_cases.create_service import CreateServiceUseCase
from app.core.use_cases.delete_service import DeleteServiceUseCase


@dataclass(slots=True)
class AppContainer:
    conn: sqlite3.Connection

    services_repo: ServicesRepo
    quotes_repo: QuickQuotesRepo

    create_quick_quote_draft: CreateQuickQuoteDraft
    add_item_to_quote: AddItemToQuote
    get_quote_details: GetQuoteDetails

    # NOVOS
    list_services: ListServicesUseCase
    create_service: CreateServiceUseCase
    delete_service: DeleteServiceUseCase

    @classmethod
    def build(cls) -> "AppContainer":
        cfg = load_config()
        conn = connect_sqlite(cfg.db_path)

        services_repo = ServicesRepo(conn)
        quotes_repo = QuickQuotesRepo(conn)

        # NOVOS USE CASES
        list_services = ListServicesUseCase(services_repo)
        create_service = CreateServiceUseCase(services_repo)
        delete_service = DeleteServiceUseCase(services_repo)

        return cls(
            conn=conn,
            services_repo=services_repo,
            quotes_repo=quotes_repo,
            create_quick_quote_draft=CreateQuickQuoteDraft(quotes_repo),
            add_item_to_quote=AddItemToQuote(quotes_repo),
            get_quote_details=GetQuoteDetails(quotes_repo),

            # NOVOS
            list_services=list_services,
            create_service=create_service,
            delete_service=delete_service,
        )

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass
