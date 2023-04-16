import warnings
import pandas as pd
from typing import Union

warnings.simplefilter("ignore")

def decoding_handler(loader):
    def inner_loader(*args, **kwargs):
        try:
            df = loader(*args, **kwargs)
        except UnicodeDecodeError:
            df = loader(*args, **kwargs, encoding="ISO-8859-1")
        return df
    return inner_loader

@decoding_handler
def load_from_file(file:str, encoding: Union[str, None]=None) -> pd.DataFrame:
    if file.endswith(".csv"):
        df = pd.read_csv(file, encoding=encoding)
    elif file.endswith(".json"):
        df = pd.read_json(file, encoding=encoding)
    elif (file.endswith(".xlsx") or file.endswith(".xls")):
        df = pd.read_excel(file)
    return df

def reformat_datetime(df: pd.DataFrame,
                      datetime_columns: Union[str, list],
                      datetime_format_in: Union[str, None]=None,
                      datetime_format_out: str="%Y-%m-%d") -> None:
    if isinstance(datetime_columns, str):
        df[datetime_columns] = pd.to_datetime(df[datetime_columns], format=datetime_format_in)
        df[datetime_columns] = df[datetime_columns].dt.strftime(datetime_format_out)
    elif isinstance(datetime_columns, list):
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col], format=datetime_format_in)
            df[col] = df[col].dt.strftime(datetime_format_out)