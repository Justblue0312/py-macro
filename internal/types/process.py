from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Literal, Optional, TypeVar

from contrib import timeit

BlockType = TypeVar("BlockType", bound="Block")
_R = TypeVar("_R", Any, Dict[str, Any])


class Block(Generic[BlockType, _R], ABC):
    def __init__(
        self,
        data: Any,
        *,
        title: Optional[str],
        description: Optional[str],
        prefix: str = "",
        mode: Literal["start", "end", ""] = "",
        **kwargs,
    ) -> None:
        self.title = title if title else self.__class__.__name__
        self.description = description
        self.prefix = prefix
        self.id = self.prefix + str(uuid.uuid4()) if self.prefix else str(uuid.uuid4())
        self.mode = mode
        self.data = data
        self.result: Optional[_R] = None

        self.kwarg = kwargs

    @abstractmethod
    @timeit(True)
    def verify(self, *args, **kwargs) -> bool:
        """Verify"""
        return True

    @abstractmethod
    @timeit(True)
    def preprocess(self, *args, **kwargs) -> bool:
        """Pre-Process"""
        if not self.verify():
            raise ValueError("Data verification failed")

    @abstractmethod
    @timeit(True)
    def process(self, *args, **kwargs) -> Optional[_R]:
        """Process"""
        if not self.preprocess():
            raise ValueError("Data pre-procession failed")
        raise NotImplementedError()
