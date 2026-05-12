from __future__ import annotations
from typing import Dict
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.memory import Memory
from tracer.action import Action, ActionType
from tracer.variable import VariableType
from tracer.state import State
from tracer.execution_fragment import ExecutionFragment
import copy

class ProgramGraph2:
    def __init__(
        self,
        initial_memory: Memory = None,
        terminal_loc: int = 0,
    ):
        # action_matrix[loc_from][loc_to] = Action
        self._action_matrix: Dict[int, Dict[int, Action]] = {}
        self._terminal_loc = terminal_loc
        #self._initial_memory = initial_memory if initial_memory is not None else Memory()

    def set_terminal_loc(self, loc: int) -> None:
        self._terminal_loc = loc

    def add_action_edge(self, loc_from: int, loc_to: int, act: Action) -> None:
        if loc_from not in self._action_matrix:
            self._action_matrix[loc_from] = {}
        self._action_matrix[loc_from][loc_to] = act

    def execute(self, _initial_memory : Memory, max_steps: int = 10000) -> ExecutionFragment:
        execution_fragment = ExecutionFragment()
        memory = Memory(
            _initial_memory.scalar_memory.__class__(
                dict(_initial_memory.scalar_memory.var_values)
            ),
            _initial_memory.array_memory.__class__(
                dict(_initial_memory.array_memory.array_values)
            ),
        )
        initial_memory_copy = copy.deepcopy(_initial_memory)
        execution_fragment.state_sequence.states.append(State(0, initial_memory_copy))
        current_loc = 0
        step_count = 0
        while current_loc != self._terminal_loc and step_count != max_steps:
            current_loc = self._do_step(current_loc, memory, execution_fragment)
            if current_loc == -1:
                return execution_fragment
            step_count += 1
        return execution_fragment

    def _do_step(
        self, loc: int, memory: Memory, execution_element: ExecutionFragment
    ) -> int:
        if loc not in self._action_matrix:
            return -1
        action_variants = self._action_matrix[loc]
        for new_loc, act in action_variants.items():
            finger_print = Action()
            if act.execute_action(memory, finger_print):
                if finger_print.type == ActionType.ASSIGN:
                    vtype = finger_print.assigned_variable.type
                    if vtype == VariableType.SCALAR_VAR:
                        finger_print.changed_value = memory.get_scalar_variable_value(
                            finger_print.assigned_variable.name
                        )
                    elif vtype == VariableType.CONCRETE_ARR_ELEMENT:
                        finger_print.changed_value = memory.get_array_element_value(
                            finger_print.assigned_variable.name,
                            finger_print.assigned_variable.index,
                        )
                execution_element.action_sequence.action_seq.append(finger_print)

                mem_copy = copy.deepcopy(memory)
                execution_element.state_sequence.states.append(State(new_loc, mem_copy))
                return new_loc
        return -1

    def to_dot(self) -> str:
        dot = ""
        for from_loc, to_map in self._action_matrix.items():
            for to_loc, act in to_map.items():
                dot += f'{from_loc} -> {to_loc} [label="{act.to_string()}"]\n'
        return "digraph G { " + dot + "}"
