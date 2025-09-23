from typing import List

import requests

from src.gpt.src.types.abc import TBaseRagClient, TBaseVectorStore, TYandexGPTBot

from .exceptions import MediatorException, MediatorInitializationException
from .types import Mode


class Mediator:
    api: requests.Session | None

    rag: TBaseRagClient | None
    gpt: TYandexGPTBot | None
    gvc: TBaseVectorStore | None

    def __init__(
        self,
        api: requests.Session = None,
        rag: TBaseRagClient = None,
        gvc: TBaseVectorStore = None,
        gpt: TYandexGPTBot = None,
    ):
        self.api = api
        self.rag = rag
        self.gvc = gvc
        self.gpt = gpt

        if api is None and (rag is None and gpt is None):
            raise MediatorInitializationException(
                "You must provide either API client or RAG class."
            )

        self.mode = (
            Mode.LOCAL if self.api is not None and self.rag is not None else Mode.API
        )

    def get_user_history(self, user_id: int) -> List:
        if self.mode == Mode.LOCAL:
            return self.gpt.get_user_history(user_id)

        if self.mode == Mode.API:
            response = requests.get(f"/history/${user_id}", timeout=5).json()
            return response

        raise MediatorException("Tried to get user history with no API or RAG client")

    def add_to_history(self, user_id: int, role: str, text: str) -> None:
        if self.mode == Mode.LOCAL:
            self.gpt.add_to_history(user_id, role, text)
            return

        if self.mode == Mode.API:
            requests.put(
                f"/history/${user_id}", {"role": role, "text": text}, timeout=5
            )
            return

        raise MediatorException(
            "Tried to update user history with no API or RAG client"
        )

    def clear_history(self, user_id: int) -> None:
        if self.mode == Mode.LOCAL:
            self.gpt.clear_history(user_id)
            return

        if self.mode == Mode.API:
            requests.delete(f"/history/${user_id}", timeout=5)
            return

        raise MediatorException("Tried to clear user history with no API or RAG client")

    def ask_gpt(self, question: str, user_id: int = None) -> str:
        if self.mode == Mode.LOCAL:
            return self.gpt.ask_gpt(question, user_id)

        if self.mode == Mode.API:
            response = requests.post(
                f"/history/${user_id}", {"question": question}, timeout=5
            )
            return response.json()

        raise MediatorException("Tried to ask gpt with no API or RAG client")

    def rag_answer(self, question: str, user_id: int = None) -> str:
        if self.mode == Mode.LOCAL:
            return self.rag.rag_answer(
                vector_store=self.gvc,
                yandex_bot=self.gpt,
                user_id=user_id,
                query=question,
            )

        if self.mode == Mode.API:
            response = requests.post(
                f"/rag/${user_id}", {"question": question}, timeout=5
            )
            return response.json()

        raise MediatorException("Tried to ask rag with no API or RAG client")
