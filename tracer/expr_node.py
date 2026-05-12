from __future__ import annotations
from enum import Enum, auto
from typing import Optional, Dict, Set
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.memory import Memory


class ExprType(Enum):
    ASSIGN_EXPR = auto()
    ADD = auto()
    SUB = auto()
    UNARY_PLUS = auto()
    UNARY_MINUS = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    EQ = auto()
    NOT_EQUAL = auto()
    TERNAR = auto()
    CHOISE = auto()
    LESS = auto()
    GREATER = auto()
    LE = auto()
    GE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    INT = auto()
    VAR = auto()
    ABSTRACT_ARITHMETIC_OP = auto()
    ABSTRACT_BOOL_OP = auto()
    ABSTRACT_CONST = auto()
    ARRAY_INDEX = auto()


class ExprNode:
    def __init__(
        self,
        type: ExprType = None,
        left: Optional["ExprNode"] = None,
        right: Optional["ExprNode"] = None,
        int_val: int = 0,
        var_name: str = "",
    ):
        self.type = type
        self.left = left
        self.right = right
        self.int_val = int_val
        self.var_name = var_name

    def equals_to(self, other: Optional["ExprNode"]) -> bool:
        if other is None:
            return False
        if self.type != other.type:
            return False
        if self.type == ExprType.INT:
            return self.int_val == other.int_val
        if self.type == ExprType.VAR:
            return self.var_name == other.var_name
        if self.type == ExprType.ABSTRACT_CONST:
            return True
        return self.left.equals_to(other.left) and self.right.equals_to(other.right)

    def to_string(self) -> str:
        t = self.type
        if t == ExprType.ASSIGN_EXPR:
            return self.left.to_string() + " = " + self.right.to_string()
        elif t == ExprType.ADD:
            return self.left.to_string() + " + " + self.right.to_string()
        elif t == ExprType.UNARY_PLUS:
            return "+ (" + self.left.to_string() + ")"
        elif t == ExprType.UNARY_MINUS:
            return "- (" + self.left.to_string() + ")"
        elif t == ExprType.SUB:
            return self.left.to_string() + " - (" + self.right.to_string() + ")"
        elif t == ExprType.MUL:
            return "(" + self.left.to_string() + ") * (" + self.right.to_string() + ")"
        elif t == ExprType.DIV:
            return "(" + self.left.to_string() + ") / (" + self.right.to_string() + ")"
        elif t == ExprType.MOD:
            return "(" + self.left.to_string() + ") % (" + self.right.to_string() + ")"
        elif t == ExprType.INT:
            return str(self.int_val)
        elif t == ExprType.VAR:
            return self.var_name
        elif t == ExprType.NOT_EQUAL:
            return self.left.to_string() + " != " + self.right.to_string()
        elif t == ExprType.LESS:
            return self.left.to_string() + " < " + self.right.to_string()
        elif t == ExprType.GREATER:
            return self.left.to_string() + " > " + self.right.to_string()
        elif t == ExprType.LE:
            return self.left.to_string() + " <= " + self.right.to_string()
        elif t == ExprType.GE:
            return self.left.to_string() + " >= " + self.right.to_string()
        elif t == ExprType.EQ:
            return self.left.to_string() + " == " + self.right.to_string()
        elif t == ExprType.AND:
            return "(" + self.left.to_string() + ") && (" + self.right.to_string() + ")"
        elif t == ExprType.OR:
            return "(" + self.left.to_string() + ") || (" + self.right.to_string() + ")"
        elif t == ExprType.TERNAR:
            return (
                "(" + self.left.to_string()
                + ") ? ( " + self.right.left.to_string()
                + " : " + self.right.right.to_string() + ")"
            )
        elif t == ExprType.NOT:
            return "! (" + self.left.to_string() + ")"
        elif t == ExprType.ABSTRACT_ARITHMETIC_OP:
            return "(" + self.left.to_string() + ") Abstract_AOP (" + self.right.to_string() + ")"
        elif t == ExprType.ABSTRACT_BOOL_OP:
            return "(" + self.left.to_string() + ") Abstract_BOP (" + self.right.to_string() + ")"
        elif t == ExprType.ABSTRACT_CONST:
            return "Abstract_CONST"
        elif t == ExprType.ARRAY_INDEX:
            return self.left.to_string() + "[" + self.right.to_string() + "]"
        return ""


# ---------- фабричные функции ----------

def copy_node(e: ExprNode) -> ExprNode:
    return ExprNode(
        type=e.type,
        left=e.left,
        right=e.right,
        int_val=e.int_val,
        var_name=e.var_name,
    )

def create_int_node(val: int) -> ExprNode:
    return ExprNode(type=ExprType.INT, int_val=val)

def create_var_node(var: str) -> ExprNode:
    return ExprNode(type=ExprType.VAR, var_name=var)

def assign(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.ASSIGN_EXPR, left=copy_node(left), right=copy_node(right))

def add(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.ADD, left=copy_node(left), right=copy_node(right))

def sub(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.SUB, left=left, right=right)

def create_unary_plus(left: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.UNARY_PLUS, left=left)

def create_unary_minus(left: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.UNARY_MINUS, left=left)

def mul(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.MUL, left=left, right=right)

def div(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.DIV, left=left, right=right)

def mod(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.MOD, left=left, right=right)

def less(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.LESS, left=left, right=right)

def not_equal(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.NOT_EQUAL, left=left, right=right)

def greater(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.GREATER, left=left, right=right)

def le(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.LE, left=left, right=right)

def ge(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.GE, left=left, right=right)

def eq(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.EQ, left=left, right=right)

def and_op(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.AND, left=left, right=right)

def or_op(left: ExprNode, right: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.OR, left=left, right=right)

def create_ternar(condition: ExprNode, true_expr: ExprNode, false_expr: ExprNode) -> ExprNode:
    choise = ExprNode(left=true_expr, right=false_expr)
    return ExprNode(type=ExprType.TERNAR, left=condition, right=choise)

def create_not_node(left: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.NOT, left=left)

def get_element_by_index(array_name: str, index_expr: ExprNode) -> ExprNode:
    return ExprNode(type=ExprType.ARRAY_INDEX, left=create_var_node(array_name), right=index_expr)


# ---------- парсинг из ОПЗ (RPN) ----------

def parse_expr_from_rpn(rpn: str) -> Optional[ExprNode]:
    stack: list[ExprNode] = []
    BINARY_OPS = {
        "+": add, "-": sub, "*": mul, "/": div, "%": mod,
        "!=": not_equal, "<": less, ">": greater,
        "<=": le, ">=": ge, "==": eq,
        "&&": and_op, "||": or_op,
    }

    for token in rpn.split():
        if token in BINARY_OPS:
            right = stack.pop()
            left = stack.pop()
            stack.append(BINARY_OPS[token](left, right))
        elif token == "_+":
            stack.append(create_unary_plus(stack.pop()))
        elif token == "_-":
            stack.append(create_unary_minus(stack.pop()))
        elif token == "=":
            left = stack.pop()
            right = stack.pop()
            stack.append(assign(left, right))
        elif token == "!":
            stack.append(create_not_node(stack.pop()))
        elif token == "[]":
            right = stack.pop()
            left = stack[-1]
            if left.type == ExprType.VAR:
                stack.pop()
                stack.append(get_element_by_index(left.var_name, right))
        elif token == "[]=":
            ind_expr = stack.pop()
            arr_name = stack.pop()
            expr = stack.pop()
            arr_element_node = get_element_by_index(arr_name.var_name, ind_expr)
            stack.append(assign(arr_element_node, expr))
        elif token == "?:":
            false_branch = stack.pop()
            true_branch = stack.pop()
            condition = stack.pop()
            stack.append(create_ternar(condition, true_branch, false_branch))
        else:
            try:
                stack.append(create_int_node(int(token)))
            except ValueError:
                stack.append(create_var_node(token))

    if len(stack) != 1:
        return None
    return stack[0]


# ---------- вспомогательные функции ----------

def expr_node_string(expr: Optional[ExprNode]) -> str:
    if expr is None:
        return ""
    return expr.to_string()


def find_expr_variables(expr: Optional[ExprNode], vars: Set[str]) -> None:
    if expr is None:
        return
    if expr.type == ExprType.VAR:
        vars.add(expr.var_name)
    find_expr_variables(expr.left, vars)
    find_expr_variables(expr.right, vars)


def get_abstract_expr_node(
    expr: Optional[ExprNode],
    abstract_const: bool = False,
    abstract_operator: bool = False,
) -> Optional[ExprNode]:
    if expr is None:
        return None

    ARITH_TYPES = {ExprType.ADD, ExprType.SUB, ExprType.MUL, ExprType.DIV}
    BOOL_TYPES = {
        ExprType.AND, ExprType.OR, ExprType.NOT,
        ExprType.LESS, ExprType.GREATER,
        ExprType.GE, ExprType.LE, ExprType.EQ,
    }

    if abstract_const and expr.type == ExprType.INT:
        return ExprNode(type=ExprType.ABSTRACT_CONST)
    elif abstract_operator and expr.type in ARITH_TYPES:
        return ExprNode(
            type=ExprType.ABSTRACT_ARITHMETIC_OP,
            left=get_abstract_expr_node(expr.left, abstract_const, abstract_operator),
            right=get_abstract_expr_node(expr.right, abstract_const, abstract_operator),
        )
    elif abstract_operator and expr.type in BOOL_TYPES:
        return ExprNode(
            type=ExprType.ABSTRACT_BOOL_OP,
            left=get_abstract_expr_node(expr.left, abstract_const, abstract_operator),
            right=get_abstract_expr_node(expr.right, abstract_const, abstract_operator),
        )
    else:
        return ExprNode(
            type=expr.type,
            var_name=expr.var_name,
            int_val=expr.int_val,
            left=get_abstract_expr_node(expr.left, abstract_const, abstract_operator),
            right=get_abstract_expr_node(expr.right, abstract_const, abstract_operator),
        )


# ---------- вычисление выражения ----------

def calc_expr_node_with_dict(node: ExprNode, var_values: Dict[str, int]) -> int:
    t = node.type
    if t == ExprType.ADD:
        return calc_expr_node_with_dict(node.left, var_values) + calc_expr_node_with_dict(node.right, var_values)
    elif t == ExprType.SUB:
        return calc_expr_node_with_dict(node.left, var_values) - calc_expr_node_with_dict(node.right, var_values)
    elif t == ExprType.UNARY_PLUS:
        return calc_expr_node_with_dict(node.left, var_values)
    elif t == ExprType.UNARY_MINUS:
        return -calc_expr_node_with_dict(node.left, var_values)
    elif t == ExprType.MUL:
        return calc_expr_node_with_dict(node.left, var_values) * calc_expr_node_with_dict(node.right, var_values)
    elif t == ExprType.DIV:
        divisor = calc_expr_node_with_dict(node.right, var_values)
        return 0 if divisor == 0 else calc_expr_node_with_dict(node.left, var_values) // divisor
    elif t == ExprType.NOT_EQUAL:
        return int(calc_expr_node_with_dict(node.left, var_values) != calc_expr_node_with_dict(node.right, var_values))
    elif t == ExprType.EQ:
        return int(calc_expr_node_with_dict(node.left, var_values) == calc_expr_node_with_dict(node.right, var_values))
    elif t == ExprType.LESS:
        return int(calc_expr_node_with_dict(node.left, var_values) < calc_expr_node_with_dict(node.right, var_values))
    elif t == ExprType.GREATER:
        return int(calc_expr_node_with_dict(node.left, var_values) > calc_expr_node_with_dict(node.right, var_values))
    elif t == ExprType.LE:
        return int(calc_expr_node_with_dict(node.left, var_values) <= calc_expr_node_with_dict(node.right, var_values))
    elif t == ExprType.GE:
        return int(calc_expr_node_with_dict(node.left, var_values) >= calc_expr_node_with_dict(node.right, var_values))
    elif t == ExprType.AND:
        return int(bool(calc_expr_node_with_dict(node.left, var_values)) and bool(calc_expr_node_with_dict(node.right, var_values)))
    elif t == ExprType.OR:
        return int(bool(calc_expr_node_with_dict(node.left, var_values)) or bool(calc_expr_node_with_dict(node.right, var_values)))
    elif t == ExprType.NOT:
        if node.right is not None:
            return 0
        return int(not calc_expr_node_with_dict(node.left, var_values))
    elif t == ExprType.INT:
        return node.int_val
    elif t == ExprType.VAR:
        return var_values.get(node.var_name, 0)
    return 0


def calc_expr_node(node: ExprNode, memory: Memory) -> int:
    t = node.type

    if t == ExprType.ARRAY_INDEX:
        idx = calc_expr_node(node.right, memory)
        return memory.array_memory.array_values[node.left.var_name].index_values[idx]
    elif t == ExprType.UNARY_PLUS:
        return calc_expr_node(node.left, memory)
    elif t == ExprType.UNARY_MINUS:
        return -calc_expr_node(node.left, memory)
    elif t == ExprType.ADD:
        return calc_expr_node(node.left, memory) + calc_expr_node(node.right, memory)
    elif t == ExprType.SUB:
        return calc_expr_node(node.left, memory) - calc_expr_node(node.right, memory)
    elif t == ExprType.MUL:
        return calc_expr_node(node.left, memory) * calc_expr_node(node.right, memory)
    elif t == ExprType.DIV:
        divisor = calc_expr_node(node.right, memory)
        return 0 if divisor == 0 else calc_expr_node(node.left, memory) // divisor
    elif t == ExprType.MOD:
        divisor = calc_expr_node(node.right, memory)
        return 0 if divisor == 0 else calc_expr_node(node.left, memory) % divisor
    elif t == ExprType.EQ:
        return int(calc_expr_node(node.left, memory) == calc_expr_node(node.right, memory))
    elif t == ExprType.NOT_EQUAL:
        return int(calc_expr_node(node.left, memory) != calc_expr_node(node.right, memory))
    elif t == ExprType.LESS:
        return int(calc_expr_node(node.left, memory) < calc_expr_node(node.right, memory))
    elif t == ExprType.GREATER:
        return int(calc_expr_node(node.left, memory) > calc_expr_node(node.right, memory))
    elif t == ExprType.LE:
        return int(calc_expr_node(node.left, memory) <= calc_expr_node(node.right, memory))
    elif t == ExprType.GE:
        return int(calc_expr_node(node.left, memory) >= calc_expr_node(node.right, memory))
    elif t == ExprType.AND:
        return int(bool(calc_expr_node(node.left, memory)) and bool(calc_expr_node(node.right, memory)))
    elif t == ExprType.OR:
        return int(bool(calc_expr_node(node.left, memory)) or bool(calc_expr_node(node.right, memory)))
    elif t == ExprType.TERNAR:
        if calc_expr_node(node.left, memory):
            return calc_expr_node(node.right.left, memory)
        else:
            return calc_expr_node(node.right.right, memory)
    elif t == ExprType.NOT:
        if node.right is not None:
            return 0
        return int(not calc_expr_node(node.left, memory))
    elif t == ExprType.INT:
        return node.int_val
    elif t == ExprType.VAR:
        return memory.scalar_memory.var_values.get(node.var_name, 0)
    return 0
