from enum import Enum
# from pydantic import BaseModel


class ModelStatus(str, Enum):
    ready = "ready"
    not_ready = "not_ready"
    initializing = "initializing"
