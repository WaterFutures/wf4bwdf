import pandas as pd
from typing import Union, List

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

HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7
HOURS_PER_WEEK = HOURS_PER_DAY * DAYS_PER_WEEK

def _check_metric_inputs(a_forecast: pd.Series, a_ground_truth: pd.Series) -> bool:
    assert isinstance(a_forecast, pd.Series), "forecast must be a pandas Series"
    assert isinstance(a_ground_truth, pd.Series), "ground_truth must be a pandas Series"
    assert len(a_forecast) == HOURS_PER_WEEK, f"forecast must be one week ({HOURS_PER_WEEK} values)"
    assert len(a_ground_truth) == HOURS_PER_WEEK, f"ground_truth must be one week ({HOURS_PER_WEEK} values)"
    assert a_forecast.name == a_ground_truth.name, f"Series names must match (same DMA). Forecast name: {a_forecast.name} | Ground truth name: {a_ground_truth.name}"
    return True

def _compute_pi1(forecast: pd.Series, ground_truth: pd.Series) -> float:
    """MAE of the first day (first 24 hours)"""
    _check_metric_inputs(a_forecast=forecast, a_ground_truth=ground_truth)
    # First day: first 24 values
    return (forecast.iloc[:HOURS_PER_DAY] - ground_truth.iloc[:HOURS_PER_DAY]).abs().mean()

def _compute_pi2(forecast: pd.Series, ground_truth: pd.Series) -> float:
    """Max Abs Error of the first day (first 24 hours)"""
    _check_metric_inputs(a_forecast=forecast, a_ground_truth=ground_truth)
    # First day: first 24 values
    return (forecast.iloc[:HOURS_PER_DAY] - ground_truth.iloc[:HOURS_PER_DAY]).abs().max()

def _compute_pi3(forecast: pd.Series, ground_truth: pd.Series) -> float:
    """MAE from the second day onward (hours 24-167)"""
    _check_metric_inputs(a_forecast=forecast, a_ground_truth=ground_truth)
    # From hour 24 to 167 (second day onward)
    return (forecast.iloc[HOURS_PER_DAY:] - ground_truth.iloc[HOURS_PER_DAY:]).abs().mean()

def _check_evaluate_inputs(
        forecast: Union[pd.DataFrame, pd.Series, List[pd.Series]],
        calendar: pd.DataFrame
        ) -> pd.DataFrame:
    # Input type check
    # Calendar comes from inside so let's assert we don't change it in the future
    assert isinstance(calendar, pd. DataFrame)
    # Forecast is provided from the user so let's fix it
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

    # All forecast datetimes must be in evaluation weeks
    eval_dates = calendar[calendar[EVALUATION_WEEK]].index
    if not forecast.index.isin(eval_dates).all():
        raise ValueError("All forecast datetimes must be within evaluation weeks.")

    # It is ok to have more then one evaluation week in the same dataframe
    # All dates in evaluation weeks appearing must be part of a complete week.
    # This is like counting how many datetimes belong to each iteration and make
    # sure that they are all exactly HOURS_PER_WEEK
    fcst_eval_dates = calendar[ITERATION].loc[forecast.index]
    counts = fcst_eval_dates.groupby(fcst_eval_dates).size()
    to_remove = []
    for iter_num, count in counts.items():
        if count != HOURS_PER_WEEK:
            # week of this iteration is incomplete.
            print(f"Warning: Evaluation week for iteration {iter_num} is incomplete (has {count} rows, expected {HOURS_PER_WEEK}). Removing these rows from forecast.")
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
    return forecast

def evaluate(forecast: Union[pd.DataFrame, pd.Series, List[pd.Series]]) -> pd.Series:
    """
    Evaluate forecast performance against ground truth data using the Battle of 
    the Water Demand Forecasting original evalutation weeks and performance indicators.
    
    This function computes three performance indicators (PI1, PI2, PI3) for each DMA (District 
    Metered Area) across different evaluation weeks by comparing forecast values against actual 
    inflow measurements. It infers automatially the evaluation week and DMA to test
    based on the input. 
    
    Parameters
    ----------
    forecast : Union[pd.DataFrame, pd.Series, List[pd.Series]]
        Forecast data to evaluate. Can be:
        - DataFrame with DMAs as columns and dates as index
        - Series with forecast values for a single DMA
        - List of Series, each representing forecasts for different DMAs
        The index should contain dates that correspond to the original evaluation weeks.
        DMA names can be either numerical or alphabetical format and only the existing ones 
        are evaluated.
    
    Returns
    -------
    pd.Series
        A MultiIndex Series with performance indicator values. The index has three levels:
        - Level 0: 'Evaluation week' name [W1, W2, W3, W4] deduced by the forecast dates
        - Level 1: DMA identifier (numerical or alphabetical name)
        - Level 2: Performance indicator name ('PI1', 'PI2', 'PI3')
        
        The Series values are the computed performance indicator scores for each 
        (evaluation_week, dma, pi) combination.
    
    Notes
    -----
    - Loads ground truth data automatically
    - Handles both numerical and alphabetical DMA naming conventions
    - Computes three performance indicators (PI1, PI2, PI3) for comprehensive evaluation
    - Deduces automatically the evaluation week and DMA(s) to test.
    
    Examples
    --------
    >>> # Evaluate a DataFrame forecast
    >>> forecast_df = pd.DataFrame(...)  # forecast data
    >>> results = evaluate(forecast_df)
    >>> print(results.loc[('W1', 'DMA 1', 'PI1')])  # Access specific result
    
    >>> # Evaluate a single DMA forecast
    >>> forecast_series = pd.Series(...)  # single DMA forecast
    >>> results = evaluate(forecast_series)
    >>> print(results.loc[('W1', 'DMA C', 'PI1')])  # Still need to access as a multi-index
    """
    # Load ground truth data
    dataset = load_complete_dataset(use_letters_for_names=False)
    calendar = dataset[CALENDAR_KEY]
    inflows = dataset["dma-inflows"]

    # Make sure the forecast is well formatted for this function
    forecast = _check_evaluate_inputs(forecast=forecast, calendar=calendar)
    
    # Prepare results
    results = []
    index_tuples = []

    # Map all forecast columns to their canonical DMA name (numerical)
    alpha_to_num = dict(zip(DMAS_ALPHABETICAL_NAMES, DMAS_NUMERICAL_NAMES))

    # For each evaluation week (iteration) in the forecast
    fcst_eval_dates = calendar[calendar[EVALUATION_WEEK]].loc[forecast.index]    
    
    for iter_num, group in fcst_eval_dates.groupby(ITERATION):
        iter_num = int(iter_num)
        week_name = EVAL_WEEKS_NAMES[iter_num-1]
        week_idx = group.index
        # For each DMA (column)
        for dma in forecast.columns:
            # Get forecast and ground truth for this week and DMA
            fcst_series = forecast.loc[week_idx, dma]
            
            # By default we used the numerical name, otherwise use the dma name to get the corresponding numerical
            gt_dma_name = dma
            if dma in DMAS_ALPHABETICAL_NAMES:
                gt_dma_name = alpha_to_num[dma]
            gt_series = inflows.loc[week_idx, gt_dma_name]
            
            # Rename the ground truth so that the series match the name and asserts work
            gt_series.name = dma
            assert fcst_series.name == gt_series.name, "Forecast and ground truth series names don't match"

            pi1 = _compute_pi1(fcst_series, gt_series)
            pi2 = _compute_pi2(fcst_series, gt_series)
            pi3 = _compute_pi3(fcst_series, gt_series)
            
            for pi_name, value in zip(PI_NAMES, [pi1, pi2, pi3]):
                index_tuples.append((week_name, dma, pi_name))
                results.append(value)

    # Build MultiIndex Series
    idx = pd.MultiIndex.from_tuples(index_tuples, names=[EVALUATION_WEEK, DMA, PI])
    return pd.Series(results, index=idx, name=PI)
