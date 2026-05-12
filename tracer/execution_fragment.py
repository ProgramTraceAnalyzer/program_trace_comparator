from __future__ import annotations
from typing import List, Set, Dict
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.variable import Variable, VariableType
from tracer.action import Action, ActionType
from tracer.action_sequence import ActionSequence
from tracer.state_sequence import StateSequence
from tracer.memory import Memory
from tracer.expr_node import ExprNode, ExprType
from tracer.pidg import PIDG


def find_all_read_variables_in_expr(
    expr: ExprNode,
    read_variables: Set[Variable],
    memory: Memory,
) -> None:
    """Рекурсивно собирает все переменные, читаемые в выражении."""
    if expr is None:
        return
    if expr.type == ExprType.VAR:
        read_variables.add(Variable(type=VariableType.SCALAR_VAR, name=expr.var_name))
    elif expr.type == ExprType.ARRAY_INDEX:
        # Индексное выражение вычисляем — получаем конкретный элемент
        from tracer.expr_node import calc_expr_node
        idx = calc_expr_node(expr.right, memory)
        read_variables.add(Variable(
            type=VariableType.CONCRETE_ARR_ELEMENT,
            name=expr.left.var_name,
            index=idx,
        ))
        find_all_read_variables_in_expr(expr.right, read_variables, memory)
        return
    find_all_read_variables_in_expr(expr.left, read_variables, memory)
    find_all_read_variables_in_expr(expr.right, read_variables, memory)


class ExecutionFragment:
    def __init__(
        self,
        state_sequence: StateSequence = None,
        action_sequence: ActionSequence = None,
    ):
        self.state_sequence = state_sequence if state_sequence is not None else StateSequence()
        self.action_sequence = action_sequence if action_sequence is not None else ActionSequence()

    def to_html(self) -> str:
        html = '<table class="table table-striped">'
        states = self.state_sequence.states
        actions = self.action_sequence.action_seq
        html += f"<tr><th>S0</th><td>{states[0].to_html()}</td></tr>"
        for i, (act, state) in enumerate(zip(actions, states[1:]), start=1):
            html += f'<tr><th>A{i - 1}</th><td>{act.to_html()}</td></tr>'
            html += f'<tr><th>S{i}</th><td>{state.to_html()}</td></tr>'
        html += "</table>"
        return html

    def find_last_variable_assign_for_action(
        self, action_index: int, var: Variable
    ) -> int:
        for i in range(action_index - 1, -1, -1):
            act = self.action_sequence.action_seq[i]
            if act.type == ActionType.ASSIGN and act.assigned_variable == var:
                return i
        return -1

    def get_sequence_read_variables(self) -> List[Set[Variable]]:
        read_seq: List[Set[Variable]] = []
        for i, act in enumerate(self.action_sequence.action_seq):
            read_variables: Set[Variable] = set()
            find_all_read_variables_in_expr(
                act.action_expr, read_variables, self.state_sequence.states[i].memory
            )
            if (act.type == ActionType.ASSIGN
                    and act.assigned_variable.type == VariableType.CONCRETE_ARR_ELEMENT):
                find_all_read_variables_in_expr(
                    act.assigned_variable.index_expr,
                    read_variables,
                    self.state_sequence.states[i].memory,
                )
            read_seq.append(read_variables)
        return read_seq

    def get_json_sequence_read_variables(self) -> str:
        read_seq = self.get_sequence_read_variables()
        parts = []
        for read_vars in read_seq:
            inner = ",".join(f'"{v.to_string()}"' for v in read_vars)
            parts.append("[" + inner + "]")
        return "[" + ",".join(parts) + "]"

    def build_pidg(self) -> PIDG:
        pidg = PIDG()
        pidg.action_sequence = self.action_sequence
        for i, act in enumerate(self.action_sequence.action_seq):
            read_variables: Set[Variable] = set()
            find_all_read_variables_in_expr(
                act.action_expr, read_variables, self.state_sequence.states[i].memory
            )
            if (act.type == ActionType.ASSIGN
                    and act.assigned_variable.type == VariableType.CONCRETE_ARR_ELEMENT):
                find_all_read_variables_in_expr(
                    act.assigned_variable.index_expr,
                    read_variables,
                    self.state_sequence.states[i].memory,
                )
            for var in read_variables:
                last_assign = self.find_last_variable_assign_for_action(i, var)
                if last_assign != -1:
                    if last_assign not in pidg.edges:
                        pidg.edges[last_assign] = {}
                    pidg.edges[last_assign][i] = var
                else:
                    if i not in pidg.initial_variables:
                        pidg.initial_variables[i] = set()
                    pidg.initial_variables[i].add(var)
        return pidg

    def build_pidg_dot(self) -> str:
        dot = "digraph G { "
        pidg = self.build_pidg()
        for i in range(len(self.action_sequence.action_seq)):
            dot += f"{i}\n"
        for from_node, to_map in pidg.edges.items():
            for to_node in to_map:
                dot += f"{from_node} -> {to_node}\n"
        for node, init_vars in pidg.initial_variables.items():
            for _ in init_vars:
                dot += f"{node} -> init\n"
        dot += "}"
        return dot

    def remove_unused_actions(self) -> ExecutionFragment:
        """
        Возвращает новый ExecutionFragment без «мёртвых» присваиваний —
        тех, чьё записанное значение нигде не читается последующими действиями
        И которые не являются последними присваиваниями соответствующей переменной
        в данном фрагменте исполнения.
        Исходный self не изменяется.
        """
        import copy

        actions = self.action_sequence.action_seq
        n = len(actions)

        # Шаг 1 — построить PIDG
        pidg = self.build_pidg()

        # Шаг 2 — определить индексы «последних» присваиваний для каждой переменной
        # (такие действия удалять нельзя, даже если их значение никуда не уходит)
        last_assign_for_var: Dict[str, int] = {}
        for i, act in enumerate(actions):
            if act.type == ActionType.ASSIGN:
                last_assign_for_var[act.assigned_variable.to_string()] = i

        last_assign_indices: Set[int] = set(last_assign_for_var.values())

        # Шаг 2 — найти индексы действий, значение которых читается хоть где-то
        # (то есть индексы, которые являются ключами в pidg.edges)
        has_reader: Set[int] = set(pidg.edges.keys())

        # Действие считается «мёртвым» если:
        # - это присваивание (ASSIGN)
        # - его результат нигде не читается (нет в has_reader)
        # - оно не является последним присваиванием данной переменной
        dead_indices: Set[int] = set()
        for i, act in enumerate(actions):
            if act.type == ActionType.ASSIGN:
                if i not in has_reader and i not in last_assign_indices:
                    dead_indices.add(i)

        if not dead_indices:
            # Ничего удалять не нужно — возвращаем глубокую копию
            return copy.deepcopy(self)

        # Шаг 3 — собрать оставшиеся действия (порядок сохраняется)
        kept_actions = [act for i, act in enumerate(actions) if i not in dead_indices]

        # Шаг 4 — переисполнить: берём начальное состояние памяти из self и
        # последовательно применяем оставшиеся действия
        import copy as _copy
        initial_memory = _copy.deepcopy(self.state_sequence.states[0].memory)
        initial_loc = self.state_sequence.states[0].location

        from tracer.state import State

        new_states = [State(initial_loc, _copy.deepcopy(initial_memory))]
        new_actions = []
        memory = _copy.deepcopy(initial_memory)

        for act in kept_actions:
            finger_print = Action()
            act.execute_action(memory, finger_print)

            # Определяем следующую локацию: берём из оригинального фрагмента
            # ту локацию, которая соответствует действию с тем же индексом
            # в оригинальной последовательности (ищем по содержимому)
            orig_idx = next(
                (i for i, a in enumerate(actions) if a is act), None
            )
            if orig_idx is not None and orig_idx + 1 < len(self.state_sequence.states):
                next_loc = self.state_sequence.states[orig_idx + 1].location
            else:
                next_loc = new_states[-1].location

            new_actions.append(finger_print)
            new_states.append(State(next_loc, _copy.deepcopy(memory)))

        # Шаг 5 — собрать и вернуть новый ExecutionFragment
        new_ef = ExecutionFragment(
            state_sequence=StateSequence(new_states),
            action_sequence=ActionSequence(new_actions),
        )
        return new_ef
