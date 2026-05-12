import pandas as pd
import numpy as np
from metrics import *

def build_similarity_matrix(
    df1,
    df2,
    strategy: SequenceDistanceMeasureStrategy = None,
    nan_strategy: str = "drop",
    fill_value: int = 0,
    **strategy_kwargs,
):
    """
    Строит матрицу попарной схожести переменных из двух DataFrame.

    Для каждой пары (col1 из df1, col2 из df2) извлекаются числовые
    последовательности и вычисляется процентная схожесть выбранной стратегией.

    Args:
        df1:              DataFrame (результат MemorySequence.to_pd_dataframe())
        df2:              DataFrame (результат MemorySequence.to_pd_dataframe())
        strategy:         экземпляр SequenceDistanceMeasureStrategy.
                          По умолчанию LCSStrategy().
        nan_strategy:     "drop" или "fill" — обработка NaN перед сравнением
        fill_value:       значение для замены NaN при nan_strategy="fill"
        **strategy_kwargs: дополнительные параметры стратегии (например,
                          match_score=3 для SmithWatermanStrategy)

    Returns:
        pandas.DataFrame с индексом = столбцы df1,
                             колонками = столбцы df2,
                             значениями = схожесть в процентах (float).
    """
    import pandas as pd

    if strategy is None:
        strategy = LCSStrategy()

    def _get_col(df, col):
        series = df[col]
        if nan_strategy == "drop":
            series = series.dropna()
        elif nan_strategy == "fill":
            series = series.fillna(fill_value)
        return series.to_numpy(dtype=np.int64)

    rows = {}
    for col1 in df1.columns:
        seq1 = _get_col(df1, col1)
        row = {}
        for col2 in df2.columns:
            seq2 = _get_col(df2, col2)
            result = strategy.do(seq1, seq2, **strategy_kwargs)
            row[col2] = round(result.similarity, 2)
        rows[col1] = row

    return pd.DataFrame(rows).T