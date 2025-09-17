import importlib.resources as resources
from pathlib import Path

import pandas as pd


def load_inflows():
    """Load inflows data from bundled package data"""
    try:

        with resources.files("wf4bwdf") as pkg_dir:
            data_path = pkg_dir.parent / "data" / "InflowData.xlsx"
            return pd.read_excel(data_path)
    except:
        # Fallback for development/local usage
        print("fallback to local")
        data_path = Path(__file__).parent.parent.parent / "data" / "InflowData.xlsx"
        return pd.read_excel(data_path)