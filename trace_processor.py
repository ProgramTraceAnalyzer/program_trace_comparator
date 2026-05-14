from tracer.execution_fragment import ExecutionFragment
from tracer.memory_sequence import MemorySequence
from tracer.variable import Variable

def get_column_values(df, column: str, remove_stutter_steps: bool = False, nan_strategy: str = "drop", fill_value: int = 0):
    """
    Извлекает значения одного столбца DataFrame как numpy array.

    Args:
        df:            pandas DataFrame (результат MemorySequence.to_pd_dataframe())
        column:        имя столбца
        nan_strategy:  "drop"  — удалить строки с NaN (по умолчанию)
                       "fill"  — заменить NaN на fill_value
        fill_value:    значение для замены NaN (используется при nan_strategy="fill")

    Returns:
        numpy.ndarray[int64]
    """
    import numpy as np

    series = df[column]
    if nan_strategy == "drop":
        series = series.dropna()
    elif nan_strategy == "fill":
        series = series.fillna(fill_value)
    else:
        raise ValueError(
            f"nan_strategy должен быть 'drop' или 'fill', получено: '{nan_strategy}'"
        )
    arr = series.to_numpy(dtype=np.int64)
    if remove_stutter_steps and len(arr) > 0:
        # Оставляем элемент, если он отличается от предыдущего
        mask = np.concatenate(([True], arr[1:] != arr[:-1]))
        arr = arr[mask]
    return arr

def remove_stutter_steps_in_memory_sequence(memory_sequence: MemorySequence) -> MemorySequence:
    pass