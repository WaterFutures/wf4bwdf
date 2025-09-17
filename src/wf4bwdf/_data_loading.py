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
        
        
def load_solutions():
    data_path = Path(__file__).parent.parent.parent / "submissions" / "BWDFCompetitorsSolutions.xlsx"
    print(data_path)
    return pd.read_excel(data_path, sheet_name=None)