import importlib.resources as resources
from pathlib import Path

import pandas as pd


def load_inflows():
    """Load inflows data from bundled package data"""
    try:
        data_path = Path(__file__).parent / "data" / "InflowData.xlsx"
        return pd.read_excel(data_path)
    except:
        # Fallback for development/local usage
        print("fallback to local")
        
        