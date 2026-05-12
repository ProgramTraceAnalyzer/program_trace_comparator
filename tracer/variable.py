from __future__ import annotations
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from tracer.expr_node import ExprNode


class VariableType(Enum):
    SCALAR_VAR = auto()
    CONCRETE_ARR_ELEMENT = auto()
    ABSTRACT_ARR_ELEMENT = auto()


class Variable:
    def __init__(
        self,
        type: VariableType = None,
        name: str = "",
        index: int = 0,
        index_expr: Optional["ExprNode"] = None,
    ):
        self.type = type
        self.name = name
        self.index = index
        self.index_expr = index_expr

    def to_string(self) -> str:
        if self.type == VariableType.SCALAR_VAR:
            return self.name
        elif self.type == VariableType.CONCRETE_ARR_ELEMENT:
            return f"{self.name}[{self.index}]"
        elif self.type == VariableType.ABSTRACT_ARR_ELEMENT:
            return f"{self.name}[{self.index_expr.to_string()}]"
        return ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Variable):
            return NotImplemented
        if self.type == VariableType.CONCRETE_ARR_ELEMENT:
            return self.type == other.type and self.name == other.name and self.index == other.index
        if self.type == VariableType.SCALAR_VAR:
            return self.type == other.type and self.name == other.name

    def __lt__(self, other: "Variable") -> bool:
        return self.to_string() < other.to_string()

    def __hash__(self) -> int:
        return hash((self.type, self.name, self.index))
