from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Tuple


class BaseVectorStore(ABC):
    @abstractmethod
    def persist(self):
        pass

    @abstractmethod
    def build(self, docs: List[Tuple[str, Dict]]):
        pass

    @abstractmethod
    def query(self, q: str, top_k=5) -> List[Dict]:
        pass


class BaseYandexGPTBot(ABC):
    @abstractmethod
    def get_user_history(self, user_id: int) -> List:
        pass

    @abstractmethod
    def add_to_history(self, user_id: int, role: str, text: str) -> None:
        pass

    @abstractmethod
    def clear_history(self, user_id: int) -> None:
        pass

    @abstractmethod
    def get_iam_token(self) -> str:
        pass

    @abstractmethod
    def unsafe_ask_gpt(self, question: str, user_id: int = None) -> str:
        pass

    @abstractmethod
    def ask_gpt(self, question: str, user_id: int = None) -> str:
        pass


class BaseRagClient(ABC):
    @abstractmethod
    def rag_answer(self, yandex_bot: BaseYandexGPTBot, query: str, user_id: int):
        pass


class Mode(Enum):
    API = ("API",)
    LOCAL = ("LOCAL",)
