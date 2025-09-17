from pathlib import Path

import holidays
import pandas as pd

DMAS_NUMERICAL_NAMES = [
    f"DMA_{i}" for i in range(1, 11)
]

DMAS_NUMERICAL_SHORTNAMES = [
    f"{i}" for i in range(1, 11)
]

DMAS_ALPHABETICAL_NAMES = [
    f"DMA_{chr(65 + i)}" for i in range(10)
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

DATE='Date'

# basic preprocessing to set the first column as the index with name date
def _preprocess_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    assert isinstance(df, pd.DataFrame) and df.columns[0].startswith("Date"
                                                                     )
    df = df.copy()
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0], format='%d/%m/%Y %H:%M')
    df = df.rename(columns={df.columns[0]: DATE})
    df = df.set_index(DATE)
    df.index = df.index.tz_localize('Europe/Rome', ambiguous= 'infer')
    return df

def _load_complete_inflows(alphabetical_names:bool=False) -> pd.DataFrame:
    """Load demand data from bundled package data. Performs cleaning and timing already"""
    assert isinstance(alphabetical_names, bool)

    inflows = pd.read_excel(INPUT_DIR/INFLOWS_FILE)
    inflows = _preprocess_date_columns(df= inflows)

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
    weather = pd.read_excel(INPUT_DIR/WEATHER_FILE)
    weather = _preprocess_date_columns(df= weather)

    weather.columns = WEATHER_FEATURES
    weather.attrs['units'] = WEATHER_UNITS

    return weather
    
TEST_WEEKS_ABSOLUTE = [82, 96, 107, 114] # Test weeks list as in Figure 1 of the calendar

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
    # - is test week
    test_week_flags = []
    # - competition iteration in which that date falls
    current_iter = 1
    iterations = []
    test_week_active = False

    for date in dates:
        cest_flags.append( date.dst() != pd.Timedelta(0) )

        if (date.date() in it_holidays) or (date.weekday() == 6) or (date.month == 11 and date.day == 3):
            holiday_flags.append(True)
        else:
            holiday_flags.append(False)

        if date.weekday() == 0 and date.hour == 0 and date.minute == 0:
            awn += 1
        absolute_week_numbers.append(awn)
        
        # Check if current date is in a test week
        if awn in TEST_WEEKS_ABSOLUTE:
            test_week_flags.append(True)
            test_week_active = True
        else:
            test_week_flags.append(False)
            # If we just finished a test week, increment iteration
            if test_week_active:
                current_iter += 1
                test_week_active = False
        iterations.append(current_iter)

    calendar_df = pd.DataFrame({
        "CEST": cest_flags,
        "Holiday": holiday_flags,
        "Dataset week number": absolute_week_numbers,
        "Iteration": iterations,
        "Test week": test_week_flags
    }, index=dates)

    return calendar_df

DMA_PROPERTIES_KEY = "dma-properties"
DMA_INFLOWS_KEY = "dma-inflows"
WEATHER_KEY = "weather"
CALENDAR_KEY = "calendar"

def load_complete_dataset(use_letters_for_names:bool=False) -> dict[str, pd.DataFrame]:
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
        use_letters_for_names:bool=False
) -> dict[str, pd.DataFrame]:
    if not isinstance(iteration, int) or iteration < 1 or iteration > 4:
        raise ValueError("iteration must be an integer between 1 and 4 inclusive")
    if not isinstance(use_letters_for_names, bool):
        raise TypeError("use_letters_for_names must be a bool")
    dataset = load_complete_dataset(use_letters_for_names=use_letters_for_names)

    # Keep only the data until that iteration release.
    filtered_dataset = {
        DMA_PROPERTIES_KEY: dataset[DMA_PROPERTIES_KEY]
    }
    mask = dataset[CALENDAR_KEY]["Iteration"] <= iteration
    for key in [DMA_INFLOWS_KEY, WEATHER_KEY, CALENDAR_KEY]:
        filtered_dataset[key] = dataset[key].loc[mask].copy()

    # Adjust the inflows dataset to remove the test data. Set the values to NaN
    mask = filtered_dataset[CALENDAR_KEY]["Test week"]
    filtered_dataset[DMA_INFLOWS_KEY].loc[mask, :] = float('nan')

    return filtered_dataset
        
def load_solutions():
    data_path = Path(__file__).parent.parent.parent / "submissions" / "BWDFCompetitorsSolutions.xlsx"
    print(data_path)
    return pd.read_excel(data_path, sheet_name=None)