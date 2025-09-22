from pathlib import Path

import holidays
import pandas as pd

DMAS_NUMERICAL_NAMES = [
    f"DMA {i}" for i in range(1, 11)
]

DMAS_NUMERICAL_SHORTNAMES = [
    f"{i}" for i in range(1, 11)
]

DMAS_ALPHABETICAL_NAMES = [
    f"DMA {chr(65 + i)}" for i in range(10)
]

DMAS_ALPHABETICAL_SHORTNAMES = [
    f"{chr(65 + i)}" for i in range(10)
]

def _load_dma_properties(alphabetical_names:bool=False) -> pd.DataFrame:
    assert isinstance(alphabetical_names, bool)

    # default: use numbers to call the dmas
    short_names = DMAS_NUMERICAL_SHORTNAMES
    long_names = DMAS_NUMERICAL_NAMES
    if alphabetical_names:
        short_names = DMAS_ALPHABETICAL_SHORTNAMES
        long_names = DMAS_ALPHABETICAL_NAMES

    dma_properties = {
        "Short name": short_names,
        "Description": [
            'Hospital district',
            'Residential district in the countryside',
            'Residential district in the countryside',
            'Suburban residential/commercial district',
            'Residential/commercial district close to the city centre',
            'Suburban district including sport facilities and office buildings',
            'Residential district close to the city centre',
            'City centre district',
            'Commercial/industrial district close to the port',
            'Commercial/industrial district close to the port'
        ],
        "Category": [
            'hospital', 'res-cside', 'res-cside',
            'suburb-res/com', 'rses/com-close',
            'suburb-sport/off', 'res-close',
            'city', 'port', 'port'
        ],
        "Population": [162, 531, 607, 2094, 7955, 1135, 3180, 2901, 425, 776],
        "Mean hourly flow (L/s/hour)": [8.4, 9.6, 4.3, 32.9, 78.3, 8.1, 25.1, 20.8, 20.6, 26.4]
    }
    dma_props_df = pd.DataFrame(dma_properties, index=long_names)
    return dma_props_df


INPUT_DIR=Path(__file__).parent / "data" 

INFLOWS_FILE='InflowData.xlsx'

DATETIME='Datetime'

def _read_and_process_ss_excel(filename: Path) -> pd.DataFrame:

    df = pd.read_excel(
        filename,
        parse_dates=[0],  # Parse first column as datetime
        date_format='%d/%m/%Y %H:%M',
        index_col=0,  # Set first column as index
        na_values=['', ' ', 'NULL', 'null', '-', 'NaN', 'nan']  # Handle various NaN representations
    )

    # Convert all columns to float64 (they should all be numeric)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')

    df.index.name = DATETIME

    # Make the datetime time zone aware so that we can have CET/CEST
    df.index = df.index.tz_localize('Europe/Rome', ambiguous='infer')

    return df
    
def _load_complete_inflows(alphabetical_names:bool=False) -> pd.DataFrame:
    """Load demand data from bundled package data. Performs cleaning and timing already"""
    assert isinstance(alphabetical_names, bool)

    inflows = _read_and_process_ss_excel(INPUT_DIR/INFLOWS_FILE)

     # default: use numbers to call the dmas
    short_names = DMAS_NUMERICAL_SHORTNAMES
    long_names = DMAS_NUMERICAL_NAMES
    if alphabetical_names:
        short_names = DMAS_ALPHABETICAL_SHORTNAMES
        long_names = DMAS_ALPHABETICAL_NAMES

    inflows.columns = long_names
    inflows.attrs['units'] = ['L/s' for _ in short_names]

    return inflows

WEATHER_FILE='WeatherData.xlsx'
WEATHER_FEATURES=['Rain', 'Temperature', 'Humidity', 'Windspeed']
WEATHER_UNITS=['mm', '°C', '%', 'km/h']

def _load_weather_data() -> pd.DataFrame:
    """Load demand data from bundled package data. Performs cleaning and timing already"""
    weather = _read_and_process_ss_excel(INPUT_DIR/WEATHER_FILE)

    weather.columns = WEATHER_FEATURES
    weather.attrs['units'] = WEATHER_UNITS

    return weather
    

EVAL_WEEKS_ABSOLUTE = [82, 96, 107, 114] # Evaluation weeks list as in Figure 1 of the calendar
N_EVAL_WEEKS = len(EVAL_WEEKS_ABSOLUTE)
EVAL_WEEKS_NAMES = [f'W{i}' for i in range(1,N_EVAL_WEEKS+1)]

# Calendar info:
CEST = 'CEST'
HOLIDAY = 'Holiday'
WEEK_NUM_ABSOLUTE = 'Dataset week number'
ITERATION = 'Iteration'
EVALUATION_WEEK = 'Evaluation week'

def _synthetize_calendar_info(dates:pd.DatetimeIndex) -> pd.DataFrame:
    """Creates a Pandas DataFrame with calendar and meta information for each measurement."""
    assert(isinstance(dates, pd.DatetimeIndex))

    # For each date, I need some properties:
    # - CEST: True if in Central European Summer Time (DST), else False
    cest_flags = []
    # - Holidays (retrieve from the package, plus sundays, plus the 3rd of November for the city's Saint)
    it_holidays = holidays.country_holidays('IT')
    holiday_flags = []
    # - week number (starting from 0, increase every monday at midnight)
    awn = 0
    absolute_week_numbers = []
    # - is Evaluation week
    eval_week_flags = []
    # - competition iteration in which that date falls
    current_iter = 1
    iterations = []
    eval_week_active = False

    for date in dates:
        cest_flags.append( date.dst() != pd.Timedelta(0) )

        if (date.date() in it_holidays) or (date.weekday() == 6) or (date.month == 11 and date.day == 3):
            holiday_flags.append(True)
        else:
            holiday_flags.append(False)

        if date.weekday() == 0 and date.hour == 0 and date.minute == 0:
            awn += 1
        absolute_week_numbers.append(awn)
        
        # Check if current date is in a Evaluation week
        if awn in EVAL_WEEKS_ABSOLUTE:
            eval_week_flags.append(True)
            eval_week_active = True
        else:
            eval_week_flags.append(False)
            # If we just finished a Evaluation week, increment iteration
            if eval_week_active:
                current_iter += 1
                eval_week_active = False
        iterations.append(current_iter)

    calendar_df = pd.DataFrame({
        CEST: cest_flags,
        HOLIDAY: holiday_flags,
        WEEK_NUM_ABSOLUTE: absolute_week_numbers,
        ITERATION: iterations,
        EVALUATION_WEEK: eval_week_flags
    }, index=dates)

    return calendar_df

DMA_PROPERTIES_KEY = "dma-properties"
DMA_INFLOWS_KEY = "dma-inflows"
WEATHER_KEY = "weather"
CALENDAR_KEY = "calendar"

def load_complete_dataset(
        use_letters_for_names:bool=False
    ) -> dict[str, pd.DataFrame]:
    """
    Load the complete dataset containing all DMA inflows, weather data, properties, and calendar information.
    
    This function loads and returns the complete dataset released as supplementary
     information after the end of the competition. It includes including
    historical DMA inflow measurements, weather observations, DMA properties, and calendar metadata.
    The complete dataset contains both training and evaluation period data, it's 
    the user responsability to handle the dataset correctly.
    
    Parameters
    ----------
    use_letters_for_names : bool, default False
        If True, uses alphabetical names for DMAs (e.g., 'DMA A', 'DMA B', 'DMA C').
        If False, uses numerical names for DMAs (e.g., 'DMA 1', 'DMA 2').
    
    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing the complete dataset with the following keys:
        - 'dma-properties': DataFrame with DMA properties and characteristics (DMA name as index):
            - "Short name": string with short name of the DMA (e.g., 'A', 'B', '3', '9')
            - "Description": string of the original documentation description of the DMAs
            - "Category": string that is a short description and can be used to tag the dmas. Use this info as a categorical
            - "Population": list of int with the population served by each DMA 
            - "Mean hourly flow (L/s/hour)": list of float with the mean hourly flow in L/s of each DMA 
        - 'dma-inflows': DataFrame with historical inflow measurements for all DMAs
        - 'weather': DataFrame with weather observation data
        - 'calendar': DataFrame with calendar information:
            - 'CEST': bool indicating if daylight savings time is active,
            - 'Holiday': bool indicating if the day is a holiday or a sunday
            - 'Dataset week number': int indicating the absolute week number in the dataset, starts from 0 and week 1 starts on the 4th of January 2021
            - 'Iteration': int indicating in which original iteration of the competition this measurement was released. Goes between 1 and 4 included, 5 indicates additional measurements not available during the competition
            - 'Evaluation week': bool indicating if the measurement is part of of the original competition evaluation weeks
    
    Raises
    ------
    TypeError
        If use_letters_for_names is not a boolean value.
    
    Notes
    -----
    - This function loads the complete dataset including evaluation period data
    - To compare your approach with the battle competitors use load_iteration_dataset() to get filtered data up to a specific iteration
    
    Examples
    --------
    >>> # Load complete dataset with numerical DMA names
    >>> dataset = load_complete_dataset()
    >>> print(dataset.keys())
    dict_keys(['dma-properties', 'dma-inflows', 'weather', 'calendar'])
    
    >>> # Load complete dataset with alphabetical DMA names
    >>> dataset = load_complete_dataset(use_letters_for_names=True)
    >>> print(dataset['dma-inflows'].columns[:3])  # First 3 DMA columns
    Index(['DMA A', 'DMA B', 'DMA C'], dtype='object')
    """
    if not isinstance(use_letters_for_names, bool):
        raise TypeError("use_letters_for_names must be a bool")
    inflows = _load_complete_inflows(alphabetical_names=use_letters_for_names)
    weather = _load_weather_data()
    
    return {
        DMA_PROPERTIES_KEY: _load_dma_properties(alphabetical_names=use_letters_for_names),
        DMA_INFLOWS_KEY: inflows,
        WEATHER_KEY: weather,
        CALENDAR_KEY: _synthetize_calendar_info(inflows.index)
    }

def load_iteration_dataset(
        iteration: int,
        use_letters_for_names:bool=False,
        keep_evaluation_week: bool=False
) -> dict[str, pd.DataFrame]:
    """
    Load dataset as it was made available during the competition until the requested
     iteration.
    
    This function include only data available up to the specified iteration as if
     you were participating again in the competition.
    
    Parameters
    ----------
    iteration : int
        The iteration number to filter data up to. Must be between 1 and 4 inclusive.
    use_letters_for_names : bool, default False
        If True, uses alphabetical names for DMAs (e.g., 'DMA A', 'DMA B', 'DMA C').
        If False, uses numerical names for DMAs (e.g., 'DMA 1', 'DMA 2').
    keep_evaluation_week: bool, default False
        If True, the week to forecast appears in the 'dma-inflow' DataFrame but all the values are NaN.
        If False, the 'dma-inflow' DataFrame is one week shorter than the calendar and the weather DataFrames. 

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary containing the complete dataset with the following keys:
        - 'dma-properties': DataFrame with DMA properties and characteristics (DMA name as index):
            - "Short name": string with short name of the DMA (e.g., 'A', 'B', '3', '9')
            - "Description": string of the original documentation description of the DMAs
            - "Category": string that is a short description and can be used to tag the dmas. Use this info as a categorical
            - "Population": list of int with the population served by each DMA 
            - "Mean hourly flow (L/s/hour)": list of float with the mean hourly flow in L/s of each DMA 
        - 'dma-inflows': DataFrame with historical inflow measurements for all DMAs
        - 'weather': DataFrame with weather observation data
        - 'calendar': DataFrame with calendar information:
            - 'CEST': bool indicating if daylight savings time is active,
            - 'Holiday': bool indicating if the day is a holiday or a sunday
            - 'Dataset week number': int indicating the absolute week number in the dataset, starts from 0 and week 1 starts on the 4th of January 2021
            - 'Iteration': int indicating in which original iteration of the competition this measurement was released. Goes between 1 and 4 included, 5 indicates additional measurements not available during the competition
            - 'Evaluation week': bool indicating if the measurement is part of of the original competition evaluation weeks
    
    Raises
    ------
    ValueError
        If iteration is not an integer or is outside the valid range [1, 4].
    TypeError
        If use_letters_for_names or keep_evaluation_week are not a boolean value.
    
    Notes
    -----
    - This function is designed to put the user in the same situation as the competitors were and simulate the same procedure
    
    Examples
    --------
    >>> # Load data up to iteration 3
    >>> dataset = load_iteration_dataset(iteration=3)
    >>> # Check that evaluation week data is masked
    >>> eval_mask = dataset['calendar']['Evaluation week']
    >>> print(dataset['dma-inflows'].loc[eval_mask].isna().all().all())
    True
    
    >>> # Load data for first iteration with alphabetical names
    >>> dataset = load_iteration_dataset(iteration=1, use_letters_for_names=True)
    >>> print(f"Data available until iteration: {dataset['calendar']['Iteration'].max()}")
    Data available until iteration: 1
    """
    if not isinstance(iteration, int) or iteration < 1 or iteration > N_EVAL_WEEKS:
        raise ValueError(f"iteration must be an integer between 1 and {N_EVAL_WEEKS} inclusive")
    if not isinstance(use_letters_for_names, bool):
        raise TypeError("use_letters_for_names must be a bool")
    if not isinstance(keep_evaluation_week, bool):
        raise TypeError("keep_evaluation_week must be a bool")

    dataset = load_complete_dataset(use_letters_for_names=use_letters_for_names)

    # Keep only the data until that iteration release.
    filtered_dataset = {
        DMA_PROPERTIES_KEY: dataset[DMA_PROPERTIES_KEY]
    }
    mask = dataset[CALENDAR_KEY][ITERATION] <= iteration
    for key in [DMA_INFLOWS_KEY, WEATHER_KEY, CALENDAR_KEY]:
        filtered_dataset[key] = dataset[key].loc[mask].copy()

    # Adjust the inflows dataset to remove the test data. Set the values to NaN
    mask = filtered_dataset[CALENDAR_KEY][EVALUATION_WEEK]
    filtered_dataset[DMA_INFLOWS_KEY].loc[mask, :] = float('nan')

    # Shorten the dataset and remove the week to forecast (it is all nans) unless
    # request from the user with the parameter
    if not keep_evaluation_week:
        filtered_dataset[DMA_INFLOWS_KEY] = filtered_dataset[DMA_INFLOWS_KEY].iloc[:-168]

    return filtered_dataset
