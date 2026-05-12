from tracer.pg_builder import cpp_to_program_graph
from tracer.execution_fragment import ExecutionFragment
from tracer.scalar_memory import ScalarMemory
from tracer.array_memory import ArrayMemory
from tracer.memory import Memory
from trace_processor import get_column_values
from metrics import LCSStrategy

cpp_file1 = r"2.cpp"
code1 = ""
with open(cpp_file1, 'r', encoding='utf-8') as f:
    code1 = f.read()

cpp_file2 = r"Task3_1__.cpp"
code2 = ""
with open(cpp_file2, 'r', encoding='utf-8') as f:
    code2 = f.read()

config_path = r"task_config.json"
test_list = []

import json
config = {}
with open(config_path, 'r', encoding="utf-8") as f:
    config = json.load(f)

for test in config["test_cases"]:
    scalar_memory = ScalarMemory()
    for var, val in test["data"].items():
        scalar_memory.var_values[var]=val
    memory = Memory(scalar_memory)
    test_list.append(memory)

#scalar_memory = ScalarMemory({"side_A":6, "side_B":27})
#memory = Memory(scalar_memory)

from compare_programs import compare_programs, compare_programs_on_test_list
print(test_list)
mapping = compare_programs_on_test_list(code1, code2, config["function_name"], test_list, True, 0.8)


#matrix = compare_programs(code1, code2, "cut_rectangle_into_squares", memory, remove_death_actions=False, strategy=LCSStrategy())

from hungarian import hungarian_mapping

#mapping = hungarian_mapping(matrix,70)

print(mapping)

#print(matrix)


