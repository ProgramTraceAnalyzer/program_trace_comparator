from __future__ import annotations
from typing import Dict


class Array:
    def __init__(self, size: int = 0, index_values: Dict[int, int] = None):
        self.size: int = size
        self.index_values: Dict[int, int] = index_values if index_values is not None else {}

    def to_html(self) -> str:
        html = '<table style="margin: 0px; padding: 0px;" class="table">'
        tr1 = ""
        tr2 = ""
        for i in range(self.size):
            if i in self.index_values:
                tr1 += f'<th style="margin: 0px; padding: 0px;">{i}</th>'
                tr2 += f'<td style="margin: 0px; padding: 0px;">{self.index_values[i]}</td>'
            else:
                tr1 += f"<th style='background: #CCCCCC; margin: 0px; padding: 0px;'>{i}</th>"
                tr2 += "<td style='background: #CCCCCC; margin: 0px; padding: 0px;'></td>"
        tr1 = f"<tr>{tr1}</tr>"
        tr2 = f"<tr>{tr2}</tr>"
        html += tr1 + tr2 + "</table>"
        return html

    def to_json(self) -> str:
        parts = [f'"{k}":{v}' for k, v in self.index_values.items()]
        return "{" + ",".join(parts) + "}"

    def equals_to(self, other: "Array") -> bool:
        return self.size == other.size and self.index_values == other.index_values

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Array):
            return NotImplemented
        return self.equals_to(other)
