import pandas as pd

from ._data_loading import load_complete_dataset, DMAS_NUMERICAL_NAMES, DMAS_ALPHABETICAL_NAMES

def evaluate(forecast: pd.DataFrame) -> pd.DataFrame:
    
    # Take the forecast, make sure is a pandas dataframe with index the dates

    # If 168 values and all of them are of an evaluation week 
    # create the multiindex with that W1, the dmas present and the 3 pi

    # if it has alphabetical names rename them to numerical 

    # Else, we will need some other method
