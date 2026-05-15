from tracer.pg_builder import cpp_to_program_graph
from tracer.execution_fragment import ExecutionFragment
from tracer.scalar_memory import ScalarMemory
from tracer.array_memory import ArrayMemory
from tracer.memory import Memory
from tracer.array_class import Array
from trace_processor import get_column_values
from metrics import LCSStrategy, DTWStrategy
import sys

cpp_file1 = sys.argv[1]
code1 = ""
with open(cpp_file1, 'r', encoding='utf-8') as f:
    code1 = f.read()

cpp_file2 = sys.argv[2]
code2 = ""
with open(cpp_file2, 'r', encoding='utf-8') as f:
    code2 = f.read()

config_path = sys.argv[3]
test_list = []

import json
config = {}
with open(config_path, 'r', encoding="utf-8") as f:
    config = json.load(f)

for test in config["test_cases"]:
    data = test["data"]
    scalar_memory = ScalarMemory()
    array_memory = ArrayMemory()
    for var, val in data.items():
        print("VALUE TYPE: ", type(val))
        if type(val) == int:
            scalar_memory.var_values[var]=val
        if type(val) == list:
            index_element = {}
            for i in range(0,len(val)):
                index_element[i] = val[i]
            arr_size = config["input_variables"][var]["size"]
            arr_obj = Array(arr_size, index_element)
            array_memory.array_values[var] = arr_obj
    memory = Memory(scalar_memory,array_memory)
    test_list.append(memory)


from compare_programs import compare_programs, compare_programs_on_test_list
print(test_list)
mapping = compare_programs_on_test_list(code1, code2, config["function_name"], test_list, True, True, 0.55, DTWStrategy(), "fill", -1)

print(mapping)