import numpy as np
import pandas as pd
import datashader as ds
import pytest


def test_dynamic_generated_function_cache(monkeypatch):
    monkeypatch.setenv("DATASHADER_NUMBA_CACHE", "1")
    n_lines = 35
    n_points = 100
    data = np.random.rand(n_lines, n_points).astype("float32")
    df = pd.DataFrame(data, columns=[f"c{i}" for i in range(n_points)])
    cvs = ds.Canvas(plot_width=n_points, plot_height=n_lines)
    agg = cvs.line(df, x=np.arange(n_points), y=df.columns.tolist(), axis=1,
                   line_width=1, agg=ds.count())
    assert agg.data.shape == (n_lines, n_points)
