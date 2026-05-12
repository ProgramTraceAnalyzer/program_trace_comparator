from __future__ import annotations
from enum import Enum, auto
from typing import Optional
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.variable import Variable, VariableType
from tracer.expr_node import ExprNode, copy_node, calc_expr_node
from tracer.memory import Memory


class ActionType(Enum):
    ASSIGN = auto()
    LOGIC = auto()
    SKIP = auto()


class Action:
    def __init__(
        self,
        type: ActionType = None,
        action_expr: Optional[ExprNode] = None,
        assigned_variable: Optional[Variable] = None,
        changed_value: int = 0,
    ):
        self.type = type
        self.action_expr = action_expr
        self.assigned_variable = assigned_variable if assigned_variable is not None else Variable()
        self.changed_value = changed_value

    def execute_action(self, memory: Memory, action_finger_print: Optional["Action"] = None) -> bool:
        if action_finger_print is not None:
            action_finger_print.type = self.type
            action_finger_print.action_expr = copy_node(self.action_expr)

        if self.type == ActionType.ASSIGN:
            if self.assigned_variable.type == VariableType.ABSTRACT_ARR_ELEMENT:
                index = calc_expr_node(self.assigned_variable.index_expr, memory)
                calc = calc_expr_node(self.action_expr, memory)
                memory.array_memory.array_values[self.assigned_variable.name].index_values[index] = calc
                if action_finger_print is not None:
                    action_finger_print.assigned_variable = Variable(
                        type=VariableType.CONCRETE_ARR_ELEMENT,
                        name=self.assigned_variable.name,
                        index=index,
                        index_expr=copy_node(self.assigned_variable.index_expr),
                    )
                return True
            elif self.assigned_variable.type == VariableType.SCALAR_VAR:
                calc = calc_expr_node(self.action_expr, memory)
                memory.scalar_memory.var_values[self.assigned_variable.name] = calc
                if action_finger_print is not None:
                    action_finger_print.assigned_variable = Variable(
                        type=VariableType.SCALAR_VAR,
                        name=self.assigned_variable.name,
                    )
                return True

        elif self.type == ActionType.LOGIC:
            return bool(calc_expr_node(self.action_expr, memory))

        return False

    def to_html(self) -> str:
        html = '<table style="margin: 0px; padding: 0px;">'
        if self.type == ActionType.ASSIGN:
            html += (
                "<tr><th>ASSIGN</th><td>"
                + self.assigned_variable.to_string()
                + "="
                + self.action_expr.to_string()
                + "</td></tr>"
            )
        elif self.type == ActionType.LOGIC:
            html += "<tr><th>LOGIC_EXPR</th><td>" + self.action_expr.to_string() + "</td></tr>"
        html += "</table>"
        return html

    def to_json(self) -> str:
        if self.type == ActionType.ASSIGN:
            json = (
                '"type":"assign", "assigned_variable":"'
                + self.assigned_variable.to_string()
                + '", "expression":"'
                + self.action_expr.to_string()
                + '"'
            )
        elif self.type == ActionType.LOGIC:
            json = '"type":"logic", "expression":"' + self.action_expr.to_string() + '"'
        else:
            json = ""
        return "{" + json + "}"

    def to_string(self, add_effect: bool = False) -> str:
        if self.type == ActionType.ASSIGN:
            s = self.assigned_variable.to_string() + " = " + self.action_expr.to_string()
            if add_effect:
                s += "\\n" + self.assigned_variable.to_string() + " -> " + str(self.changed_value)
            return s
        elif self.type == ActionType.LOGIC:
            return self.action_expr.to_string()
        elif self.type == ActionType.SKIP:
            return "skip"
        return ""


# ---------- фабричные функции ----------

def create_assign_action(var: Variable, assign_expr: ExprNode) -> Action:
    return Action(
        type=ActionType.ASSIGN,
        action_expr=copy_node(assign_expr),
        assigned_variable=var,
    )

def create_logic_action(logic_expr: ExprNode) -> Action:
    return Action(type=ActionType.LOGIC, action_expr=copy_node(logic_expr))

def create_skip_action() -> Action:
    return Action(type=ActionType.SKIP)
