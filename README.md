# TabularCompare

[![Python package](https://github.com/erich-hs/tabularcompare/actions/workflows/python-package.yml/badge.svg)](https://github.com/erich-hs/tabularcompare/actions/workflows/python-package.yml) [![PyPI license](https://img.shields.io/pypi/l/tabularcompare)](https://pypi.python.org/pypi/tabularcompare/) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/tabularcompare.svg)](https://img.shields.io/pypi/pyversions/tabularcompare) ![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

Tabular data comparison wrapper for [DataComPy](https://capitalone.github.io/datacompy/).

## Quick Install
```bash
pip install tabularcompare
```

## Basic Usage

### Comparison object
```python
import pandas as pd
from tabularcompare import Comparison

df1 = pd.DataFrame(
    {
        "idx1": ["A", "B", "B", "C"],
        "idx2": ["01", "01", "02", "03"],
        "colA": ["AA", "BA", "BB", "CA"],
        "colB": [100, 200, 200, 300]
     }
)
df2 = pd.DataFrame(
    {
        "idx1": ["A", "B", "C"],
        "idx2": ["01", "01", "03"],
        "colA": ["AA", "XA", "CA"],
        "colB": [101, 200, 300],
        "colC": ["foo", "bar", "baz"]
     }
)

comparison = Comparison(
    df1, df2, join_columns=["idx1", "idx2"]
)
```
### Added Functionalities
- #### Diverging Subset
This method introduces an enhanced look at the changes identified at the intersection of compared DataFrames, following the notation ```{df1} --> {df2}```.
```python
comparison.diverging_subset()
```
|   | idx1 | idx2 |          colA |            colB |
|:-:|-----:|-----:|--------------:|----------------:|
| 0 | A    | 01   | NaN           | {100} --> {101} |
| 1 | B    | 01   | {BA} --> {XA} | NaN             |

Rows that are unique to either DataFrame can be called via ```.df1_unq_rows()``` and ```.df2_unq_rows()``` methods.

```python
comparison.df1_unq_rows()
```
|   | idx1 | idx2 |	colA | colB |
|:-:|-----:|-----:|-----:|-----:|
| 2 |	B  |  02  |  BB  |	200 |

Columns that are unique to either DataFrame can be called via ```.df1_unq_columns()``` and ```.df2_unq_columns()``` methods.

```python
comparison.df2_unq_columns()
```
|   | idx1 | idx2 |	 colC |
|:-:|-----:|-----:|------:|
| 0 |	A  |  01  |  foo  |
| 1 |	B  |  01  |  bar  |
| 2 |	C  |  03  |  baz  |

- #### Enhanced Reporting
The report functionality is now callable from the comparison object. It includes a .txt, .html, and .xlsx version.
```python
comparison.report_to_txt("./results/Report.txt")
comparison.report_to_html("./results/Report.html")
comparison.report_to_xlsx("./results/Report.xlsx", write_originals=True)
```
The Excel report will output complete comparison results, with tabs dedicated to:
* Original dataframes (when ```write_originals=True```).
* Columns present only on df1 and/or df2.
* Rows present only on df1 and/or df2.
* Diverging subset showing all the changes identified from df1 to df2.

The HTML report will also output a rendered table of the diverging subset on top of the file, alongside the native DataComPy summary report.

- #### Fully-fledged [Command Line Interface](#CLI)
---
### DataComPy Methods
Most methods native to ```datacompy.Compare``` functionality are still present, including;
* ```.report()```
* ```.df1_unq_rows()``` / ```.df2_unq_rows()```
* ```.df1_unq_columns()``` / ```.df2_unq_columns()```
* ```.intersect_columns()```
* ```.intersect_rows()```

The native ```datacompy.Compare``` method is also callable from the ```tabularcompare``` core module:
```python
from tabularcompare import Compare

# datacompy.Compare method
comparison = Compare(
    df1, df2, join_columns=["idx1", "idx2"]
)
print(comparison.report())
```
For a complete documentation on DataComPy you can head to [DataComPy](https://capitalone.github.io/datacompy/).

-----
## CLI
Command Line Interface to output an Excel .xlsx report and, optionally, html and txt summaries.
```bash
tabularcompare --help
```

```
Usage: tabularcompare [OPTIONS] DF1 DF2

Options:
  -c, --columns, --on TEXT    Comma-separated list of key column(s) to compare
                              df1 against df2. When not provided, df1 and df2
                              will be matched on index.
  -ic, --ignore_columns TEXT  Comma-separated list of column(s) to ignore from
                              df1 and df2.
  -n1, --df1_name TEXT        Alias for Data frame 1. Default = df1
  -n2, --df2_name TEXT        Alias for Data frame 2. Default = df2
  -is, --ignore_spaces        Flag to strip and ignore whitespaces from string
                              columns.
  -ci, --case_insensitive     Flag to compare string columns on a case-
                              insensitive manner.
  -cl, --cast_lowercase       Flag to cast column names to lower case before
                              comparison.
  -at, --abs_tol FLOAT        Absolute tolerance between two numeric values.
  -rt, --rel_tol FLOAT        Relative tolerance between two numeric values.
  -txt, --txt                 Flag to output a .txt report with a comparison
                              summary.
  -html, --html               Flag to output an HTML report with a comparison
                              summary.
  -od, --only_deltas          Flag to suppress original dataframes from the
                              output .xlsx report.
  -o, --output, --out PATH    Output location for report files. Defaults to
                              current location.
  -e, --encoding TEXT         Character encoding to read df1 and df2.
  -v, --verbose               Verbosity.
  --help                      Show this message and exit.
```

### Sample usage
The application reads from two file paths input for csv, json, or excel files.
```bash
cd ./data/
tabularcompare ./df1.csv ./df2.csv -c 'idx1,idx2' -n1 myTable1 -n2 myTable2 -o ../results/
```

-----
## Caveat
> The comparison results will take into account data types across columns. I.E. If we update our sample dataframe df2 to include a missing value on colB, it will now be of dtype ```object```, as oposed to ```Int64``` in df1. This might lead to miss-leading interpretations of the results to users without information on data types.

```python
import pandas as pd
from tabularcompare import Comparison

df1 = pd.DataFrame(
    {
        "idx1": ["A", "B", "B", "C"],
        "idx2": ["01", "01", "02", "03"],
        "colA": ["AA", "BA", "BB", "CA"],
        "colB": [100, 200, 200, 300]
     }
)
df2 = pd.DataFrame(
    {
        "idx1": ["A", "B", "C"],
        "idx2": ["01", "01", "03"],
        "colA": ["AA", "XA", "CA"],
        "colB": [pd.NA, 200, 300],
        "colC": ["foo", "bar", "baz"]
     }
)

comparison = Comparison(
    df1, df2, join_columns=["idx1", "idx2"]
)
comparison.diverging_subset()
```
Which will return:
|   | idx1 | idx2 |          colA |            colB |
|:-:|-----:|-----:|--------------:|----------------:|
| 0 | A    | 01   | NaN           | {100} --> {}    |
| 1 | B    | 01   | {BA} --> {XA} | {200} --> {200} |
| 3 | C    | 03   | NaN           | {300} --> {300} |
