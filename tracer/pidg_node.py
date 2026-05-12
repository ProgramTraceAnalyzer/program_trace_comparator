from __future__ import annotations
from typing import Dict, Optional, TYPE_CHECKING
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.expr_node import ExprNode, get_abstract_expr_node


class PIDGNode:
    def __init__(
        self,
        id: int = 0,
        is_final: bool = False,
        assign_var: str = "",
        expr: Optional[ExprNode] = None,
        parent_nodes_by_var: Dict[str, "PIDGNode"] = None,
    ):
        self.id = id
        self.is_final = is_final
        self.assign_var = assign_var
        self.expr = expr
        self.parent_nodes_by_var: Dict[str, "PIDGNode"] = parent_nodes_by_var if parent_nodes_by_var is not None else {}

    def to_string(self) -> str:
        return self.assign_var + " = " + self.expr.to_string()

    def equals_to(self, other: Optional["PIDGNode"]) -> bool:
        if other is None:
            return False
        if self.assign_var != other.assign_var:
            return False
        if self.expr.equals_to(other.expr):
            for key, node in self.parent_nodes_by_var.items():
                if key not in other.parent_nodes_by_var:
                    return False
                if not node.equals_to(other.parent_nodes_by_var[key]):
                    return False
            for key in other.parent_nodes_by_var:
                if key not in self.parent_nodes_by_var:
                    return False
            return True
        return False


def get_abstract_pidg_node(
    node: PIDGNode,
    abstract_const: bool = False,
    abstract_operator: bool = False,
) -> PIDGNode:
    abstracted = PIDGNode(
        id=node.id,
        is_final=node.is_final,
        assign_var=node.assign_var,
        expr=get_abstract_expr_node(node.expr, abstract_const, abstract_operator),
    )
    for key, parent in node.parent_nodes_by_var.items():
        abstracted.parent_nodes_by_var[key] = get_abstract_pidg_node(parent, abstract_const, abstract_operator)
    return abstracted
