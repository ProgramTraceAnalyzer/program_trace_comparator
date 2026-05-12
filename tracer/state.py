from __future__ import annotations
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from tracer.memory import Memory


class State:
    def __init__(self, location: int = 0, memory: Memory = None):
        self.location = location
        self.memory = memory if memory is not None else Memory()

    def to_html(self) -> str:
        return (
            '<table style="margin: 0px; padding: 0px;" class="table">'
            "<tr><th>Location</th><th>Scalar Memory</th><th>Array Memory</th></tr> "
            f"<tr><td>{self.location}</td>"
            f"<td>{self.memory.scalar_memory.to_html()}</td>"
            f"<td>{self.memory.array_memory.to_html()}</td></tr>"
            "</table>"
        )

    def to_json(self) -> str:
        return (
            '{"location":'
            + str(self.location)
            + ',"memory":'
            + self.memory.to_json()
            + "}"
        )
