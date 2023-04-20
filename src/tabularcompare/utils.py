import os
import click
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


def cli_exception_handler(func):
    def inner_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            click.echo(click.style(f"{type(e).__name__}: {e}", fg="red"))

    return inner_func


@decoding_handler
def load_from_file(file: str, encoding: Union[str, None] = None) -> pd.DataFrame:
    if file.endswith(".csv"):
        df = pd.read_csv(file, encoding=encoding)
    elif file.endswith(".json"):
        df = pd.read_json(file, encoding=encoding)
    elif file.endswith(".xlsx") or file.endswith(".xls"):
        df = pd.read_excel(file)
    return df


def reformat_datetime(
    df: pd.DataFrame,
    datetime_columns: Union[str, list],
    datetime_format_in: Union[str, None] = None,
    datetime_format_out: str = "%Y-%m-%d",
) -> None:
    if isinstance(datetime_columns, str):
        df[datetime_columns] = pd.to_datetime(
            df[datetime_columns], format=datetime_format_in
        )
        df[datetime_columns] = df[datetime_columns].dt.strftime(datetime_format_out)
    elif isinstance(datetime_columns, list):
        for col in datetime_columns:
            df[col] = pd.to_datetime(df[col], format=datetime_format_in)
            df[col] = df[col].dt.strftime(datetime_format_out)


@cli_exception_handler
def report_to_xlsx(comparison, only_deltas, verbose, output):
    output_xlsx = (
        f"{comparison.df1_name}_to_{comparison.df2_name}_comparison_report.xlsx"
    )
    write_originals = not only_deltas
    if verbose:
        print(f"Writing .xlsx report to {os.path.join(output, output_xlsx)}...")
    comparison.report_to_xlsx(
        file_name=output_xlsx, file_location=output, write_originals=write_originals
    )
    xlsx_complete_msg = f"Comparison .xlsx report written to {os.path.abspath(os.path.join(output, output_xlsx))}"
    click.echo(click.style(xlsx_complete_msg, fg="green"))


@cli_exception_handler
def report_to_txt(comparison, verbose, output):
    output_txt = f"{comparison.df1_name}_to_{comparison.df2_name}_comparison_report.txt"
    if verbose:
        print(f"Writing .txt report to {os.path.join(output, output_txt)}...")
    comparison.report_to_txt(file_name=output_txt, file_location=output)
    txt_complete_msg = f"Comparison .txt report written to {os.path.abspath(os.path.join(output, output_txt))}"
    click.echo(click.style(txt_complete_msg, fg="green"))


@cli_exception_handler
def report_to_html(comparison, verbose, output):
    output_html = (
        f"{comparison.df1_name}_to_{comparison.df2_name}_comparison_report.html"
    )
    if verbose:
        print(f"Writing HTML report to {os.path.join(output, output_html)}...")
    comparison.report_to_html(file_name=output_html, file_location=output)
    html_complete_msg = f"Comparison HTML report written to {os.path.abspath(os.path.join(output, output_html))}"
    click.echo(click.style(html_complete_msg, fg="green"))
