from __future__ import annotations

from typing import List, Optional

from ..clients import LiveServerSession

try:
    from src.gpt.src.types.abc import TBaseRagClient, TBaseVectorStore, TYandexGPTBot
except ImportError:
    TBaseRagClient = None
    TBaseVectorStore = None
    TYandexGPTBot = None

from .exceptions import MediatorException, MediatorInitializationException
from .types import Mode


class Mediator:
    api: Optional[LiveServerSession]
    rag: Optional["TBaseRagClient"]
    gpt: Optional["TYandexGPTBot"]
    gvc: Optional["TBaseVectorStore"]

    def __init__(
        self,
        api: LiveServerSession,
        rag: "TBaseRagClient",
        gvc: "TBaseVectorStore",
        gpt: "TYandexGPTBot",
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
            Mode.LOCAL if (self.rag is not None and self.gpt is not None) else Mode.API
        )

    def get_user_history(self, user_id: int) -> List:
        if self.mode == Mode.LOCAL:
            return self.gpt.get_user_history(user_id)

        if self.mode == Mode.API:
            response = self.api.get(f"/history/{user_id}", timeout=15).json()
            return response["answer"]

        raise MediatorException("Tried to get user history with no API or RAG client")

    def add_to_history(self, user_id: int, role: str, text: str) -> None:
        if self.mode == Mode.LOCAL:
            self.gpt.add_to_history(user_id, role, text)
            return

        if self.mode == Mode.API:
            self.api.put(
                f"/history/{user_id}", json={"role": role, "text": text}, timeout=15
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
            self.api.delete(f"/history/{user_id}", timeout=15)
            return

        raise MediatorException("Tried to clear user history with no API or RAG client")

    def ask_gpt(self, question: str, user_id: int = None) -> str:
        if self.mode == Mode.LOCAL:
            return self.gpt.ask_gpt(question, user_id)

        if self.mode == Mode.API:
            response = self.api.post(
                f"/gpt/{user_id}", json={"question": question}, timeout=15
            )
            return response.json()["answer"]

        raise MediatorException("Tried to ask gpt with no API or RAG client")

    def rag_answer(self, question: str) -> str:
        if self.mode == Mode.LOCAL:
            return self.rag.rag_answer(
                vector_store=self.gvc,
                yandex_bot=self.gpt,
                user_id=None,
                query=question,
            )

        if self.mode == Mode.API:
            response = self.api.post("/rag/", json={"question": question}, timeout=15)
            return response.json()["answer"]

        raise MediatorException("Tried to ask rag with no API or RAG client")
