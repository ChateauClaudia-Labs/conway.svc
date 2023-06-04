import pandas                                   as _pd
from pathlib                                    import Path

def parallel_load_excel(path, sheet_name):
    if Path(path).exists():
        df = _pd.read_excel(path, sheet_name)
        return df
    else:
        return None