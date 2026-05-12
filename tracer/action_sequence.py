from __future__ import annotations
from typing import List
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.action import Action


class ActionSequence:
    def __init__(self, action_seq: List[Action] = None):
        self.action_seq: List[Action] = action_seq if action_seq is not None else []

    def to_html(self) -> str:
        html = "<table>"
        for num, action in enumerate(self.action_seq):
            html += f"<tr><th>{num}</th><td>{action.to_html()}</td></tr>"
        html += "</table>"
        return html

    def to_json(self) -> str:
        parts = [a.to_json() for a in self.action_seq]
        return "[" + ",".join(parts) + "]"
