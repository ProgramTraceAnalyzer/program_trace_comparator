from __future__ import annotations
from typing import List
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.state import State
from tracer.memory_sequence import MemorySequence


class StateSequence:
    def __init__(self, states: List[State] = None):
        self.states: List[State] = states if states is not None else []

    def to_html(self) -> str:
        html = "<table>"
        for num, state in enumerate(self.states):
            html += f"<tr><th>{num}</th><td>{state.to_html()}</td></tr>"
        html += "</table>"
        return html

    def to_json(self) -> str:
        parts = [s.to_json() for s in self.states]
        return "[" + ",".join(parts) + "]"

    def get_memory_sequence(self) -> MemorySequence:
        ms = MemorySequence()
        for state in self.states:
            ms.memory_seq.append(state.memory)
        return ms
