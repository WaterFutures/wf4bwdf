import pandas as pd

from ._data_loading import load_complete_dataset
from ._data_loading import DMAS_NUMERICAL_NAMES, DMAS_ALPHABETICAL_NAMES
from ._data_loading import EVALUATION_WEEK, EVAL_WEEKS_NAMES
from ._data_loading import DATETIME, CALENDAR_KEY, ITERATION

DMA = 'DMA'
PI = 'BWDF performance indicator'
PI1 = 'PI1'
PI2 = 'PI2'
PI3 = 'PI3'
PI_NAMES = [PI1, PI2, PI3]

def evaluate(forecast: pd.DataFrame) -> pd.Series:
    
    # Input type check
    if isinstance(forecast, pd.Series):
        forecast = forecast.to_frame()
    elif isinstance(forecast, list) and all(isinstance(s, pd.Series) for s in forecast):
        forecast = pd.concat(forecast, axis=1)
    elif not isinstance(forecast, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame, Series, or list of Series.")

    # If first column is 'Date', set as index
    if forecast.index.name is None or not pd.api.types.is_datetime64_any_dtype(forecast.index):
        if forecast.columns[0].lower() == DATETIME.lower():
            forecast = forecast.copy()
            forecast[forecast.columns[0]] = pd.to_datetime(forecast[forecast.columns[0]], errors='raise')
            forecast = forecast.set_index(forecast.columns[0])
        else:
            raise ValueError(f"Forecast must have a DatetimeIndex or a '{DATETIME}' column as the first column.")

    # Dates must be unique
    if not forecast.index.is_unique:
        raise ValueError("Datetime index must have unique values.")

    # Load calendar info for evaluation weeks
    calendar = load_complete_dataset()[CALENDAR_KEY]
    eval_dates = calendar[calendar[EVALUATION_WEEK]].index

    # All forecast datetimes must be in evaluation weeks
    if not forecast.index.isin(eval_dates).all():
        raise ValueError("All forecast datetimes must be within evaluation weeks.")

    # It is ok to have more then one evaluation week in the same dataframe
    # All dates in evaluation weeks appearing must be part of a complete week.
    # This is like counting how many datetimes belong to each iteration and make
    # sure that they are all exactly 168
    fcst_eval_dates = calendar[ITERATION].loc[forecast.index]
    counts = fcst_eval_dates.groupby(ITERATION).size()
    to_remove = []
    for iter_num, count in counts.items():
        if count != 168:
            # week of this iteration is incomplete.
            print(f"Warning: Evaluation week for iteration {iter_num} is incomplete (has {count} rows, expected 168). Removing these rows from forecast.")
            # Mark all indices for this incomplete iteration for removal
            idx_to_remove = fcst_eval_dates[fcst_eval_dates == iter_num].index
            to_remove.extend(idx_to_remove)
    if to_remove:
        forecast = forecast.drop(index=to_remove)
        if forecast.empty:
            raise ValueError("All evaluation weeks in the forecast are incomplete. No data left after removal.")        

    # Columns: must be subset of DMAS_NUMERICAL_NAMES or DMAS_ALPHABETICAL_NAMES
    valid_dmas = set(DMAS_NUMERICAL_NAMES) | set(DMAS_ALPHABETICAL_NAMES)
    forecast_cols = set(forecast.columns)
    unrecognized = forecast_cols - valid_dmas
    if unrecognized:
        print(f"Warning: Unrecognized DMA columns skipped: {unrecognized}")
    # Keep only recognized columns
    recognized = [col for col in forecast.columns if col in valid_dmas]
    if not recognized:
        raise ValueError("No recognized DMA columns found in forecast.")
    forecast = forecast[recognized]

    # If alphabetical names, rename to numerical
    if any(col in DMAS_ALPHABETICAL_NAMES for col in forecast.columns):
        alpha_to_num = dict(zip(DMAS_ALPHABETICAL_NAMES, DMAS_NUMERICAL_NAMES))
        forecast = forecast.rename(columns=alpha_to_num)

    # Return a placeholder result for now
    return pd.Series([0.0]*len(forecast), index=forecast.index, name="evaluation_placeholder")


