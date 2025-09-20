from pathlib import Path

import pandas as pd

from ._data_loading import DATETIME, DMAS_NUMERICAL_NAMES

def _read_and_process_bwdf_competitors_solutions(filename: Path) -> dict[str, pd.DataFrame]:

    solutions = pd.read_excel(
        filename,
        usecols=list(range(1,12)), # Skip the first column 'Evaluation week'
        parse_dates={DATETIME: [0]},  # Parse second column as datetime
        date_format='%d/%m/%Y %H:%M',
        index_col=0,  # Set first column as index
        na_values=['', ' ', 'NULL', 'null', '-', 'NaN', 'nan'],  # Handle various NaN representations
        sheet_name=None
    )

    # We have a dictionary with an entry for each sheet
    for key, df in solutions.items():
        # Convert all columns to float64 (they should all be numeric)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')

        df.columns = DMAS_NUMERICAL_NAMES
        df.attrs['units'] = ['L/s' for _ in DMAS_NUMERICAL_NAMES]

        # Make the datetime time zone aware so that we can have CET/CEST
        df.index = df.index.tz_localize('Europe/Rome', ambiguous='infer')

    return solutions