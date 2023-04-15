import click
from utils import load_from_file
from compare import Comparison

#TODO:
'''
- Verbosity
- Handle identical dataframes and exit
- Handle file is already open (PermissionError)
- Handle df with collumn full of null values, while the other has valid values
- Handle missing columns from join_columns in df1 or df2
'''

@click.command()
@click.argument('df1', type=click.Path(exists=True), required=True)
@click.argument('df2', type=click.Path(exists=True), required=True)
@click.option('-c', '--columns', '--on', help='Comma-separated list of key column(s) to compare df1 against df2. When not provided, df1 and df2 will be matched on index.')
@click.option('-ic', '--ignore_columns', help='Comma-separated list of column(s) to ignore from df1 and df2.')
@click.option('-n1', '--df1_name', default='df1', help='Alias for Data frame 1. Default = df1')
@click.option('-n2', '--df2_name', default='df2', help='Alias for Data frame 2. Default = df2')
@click.option('-is', '--ignore_spaces', is_flag=True, help='Flag to strip and ignore whitespaces from string columns.')
@click.option('-ci', '--case_insensitive', is_flag=True, help='Flag to compare string columns on a case-insensitive manner.')
@click.option('-txt', '--txt', is_flag=True, help='Flag to output a .txt report with a comparison summary.')
@click.option('-html', '--html', is_flag=True, help='Flag to output an HTML report with a comparison summary.')
@click.option('-od', '--only_deltas', is_flag=True, help='Flag to suppress original dataframes from the output .xlsx report.')
@click.option('-o', '--output', '--out', type=click.Path(exists=True), default='.', help='Output location for report files. Defaults to current location.')
def cli(df1,
        df2,
        columns,
        ignore_columns,
        df1_name,
        df2_name,
        ignore_spaces,
        case_insensitive,
        txt,
        html,
        only_deltas,
        output):
    df1 = load_from_file(df1)
    df2 = load_from_file(df2)

    # Join params
    if columns:
        join_columns = [col.strip() for col in columns.split(',')]
        on_index = False
    else:
        join_columns = None
        on_index = True

    if ignore_columns:
        ignore_columns = [col.strip() for col in ignore_columns.split(',')]

    # Comparison object
    comparison = Comparison(
        df1=df1,
        df2=df2,
        join_columns=join_columns,
        ignore_columns=ignore_columns,
        on_index=on_index,
        df1_name=df1_name,
        df2_name=df2_name,
        ignore_spaces=ignore_spaces,
        ignore_case=case_insensitive,
        cast_column_names_lower=False
    )

    # Reporting
    output_xlsx = f"{df1_name}_to_{df2_name}_comparison_report.xlsx"
    write_originals = not only_deltas
    comparison.report_to_xlsx(file_name=output_xlsx, file_location=output, write_originals=write_originals)
    if txt:
        output_txt = f"{df1_name}_to_{df2_name}_comparison_report.txt"
        comparison.report_to_txt(file_name=output_txt, file_location=output)
    if html:
        output_html = f"{df1_name}_to_{df2_name}_comparison_report.html"
        comparison.report_to_html(file_name=output_html, file_location=output)

if __name__=="__main__":
    cli()