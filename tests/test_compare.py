import pytest
import numpy as np
import pandas as pd
from tabularcompare import compare

# Test parameters
@pytest.fixture
def create_test_data():
    df1 = pd.DataFrame(
        {"idx1": [1, 1, 2, 3, 3, 4],
        "idx2": ["A", "B", "A", "A", "B", "A"],
        "fname": ["Nikola", "Nikola", "Albert", "Stephen", "Stephen", "Steve"],
        "lname": ["Tesla", "Tesla", "Einstein", "Hawking", "Hawking", "Jobs"],
        "emptycol": [pd.NA for i in range(6)],
        "email": ["em@tesla.com", "em@spacex.com", "ae@gmail.com", "sh@cam.uk", pd.NA, "sj@apple.com"],
        "dob": ["1856-07-10", "1856-07-10", "1879-03-14", "1942-01-08", "1942-01-08", "1955-02-24"],
        "active": [True, False, True, True, False, True]}
    )
    df1["dob"] = pd.to_datetime(df1["dob"])
    df2 = pd.DataFrame(
        {"idx1": [1, 1, 2, 3, 3, 2],
        "idx2": ["A", "B", "A", "A", "B", "A"],
        "fname": ["Nick", "Nick", "Albert", "Stephen", "Stephen", "Albert"],
        "lname": ["Tesla", "Tesla", "Einstein", "Hawking", "Hawking", "Einstein"],
        "emptycol": [pd.NA for i in range(6)],
        "email": ["em@tesla.com", "em@spacex.com", "ae@gmail.com", "sh@cam.uk", pd.NA, "ae@hotmail.com"],
        "dob": ["1856-07-10", pd.NA, "1879-03-14", "1942-03-08", "1942-01-08", "1879-03-14"],
        "active": [True, False, True, True, False, pd.NA]}
    )
    df2["dob"] = pd.to_datetime(df2["dob"])
    join_columns = ["idx1", "idx2"]
    return df1, df2, join_columns

def test_report(create_test_data: tuple):
    expected_partial_report = 'DataComPy Comparison\n--------------------\n\nDataFrame Summary\n-----------------\n\n  DataFrame  Columns  Rows\n0       df1        8     6\n1       df2        8     6\n\nColumn Summary\n--------------\n\nNumber of columns in common: 8\nNumber of columns in df1 but not in df2: 0\nNumber of columns in df2 but not in df1: 0\n\nRow Summary\n-----------\n\nMatched on: idx1, idx2\nAny duplicates on match values: Yes\nAbsolute Tolerance: 0\nRelative Tolerance: 0\nNumber of rows in common: 5\nNumber of rows in df1 but not in df2: 1\nNumber of rows in df2 but not in df1: 1\n\nNumber of rows with some compared columns unequal: 3\nNumber of rows with all compared columns equal: 2\n\nColumn Comparison\n-----------------\n\nNumber of columns compared with some values unequal: 2\nNumber of columns compared with all values equal: 6\nTotal number of values which compare unequal: 4\n\nColumns with Unequal Values or Types\n------------------------------------'
    df1, df2, join_columns = create_test_data
    comparison = compare.Comparison(df1, df2, join_columns)
    report = comparison.report()
    assert expected_partial_report in report

def test_diverging_subset(create_test_data: tuple):
    expected_diverging_subset = pd.DataFrame(
    {'idx1': {0: 1, 1: 1, 3: 3},
     'idx2': {0: 'A', 1: 'B', 3: 'A'},
     'fname': {0: '{Nikola} --> {Nick}', 1: '{Nikola} --> {Nick}', 3: np.nan},
     'dob': {0: np.nan,
             1: '{1856-07-10} --> {NaT}',
             3: '{1942-01-08} --> {1942-03-08}'}}
    )
    df1, df2, join_columns = create_test_data
    comparison = compare.Comparison(df1, df2, join_columns)
    diverging_subset = comparison.diverging_subset()
    assert diverging_subset.equals(expected_diverging_subset)

def test_df1_unq_columns(create_test_data: tuple):
    expected_df1_unq_columns = pd.DataFrame(
    {'idx1': {0: 1, 1: 1, 2: 2, 3: 3, 4: 3, 5: 4},
     'idx2': {0: 'A', 1: 'B', 2: 'A', 3: 'A', 4: 'B', 5: 'A'}}
    )
    df1, df2, join_columns = create_test_data
    comparison = compare.Comparison(df1, df2, join_columns)
    df1_unq_columns = comparison.df1_unq_columns()
    assert df1_unq_columns.equals(expected_df1_unq_columns)

def test_df2_unq_columns(create_test_data: tuple):
    expected_df2_unq_columns = pd.DataFrame(
    {'idx1': {0: 1, 1: 1, 2: 2, 3: 3, 4: 3, 5: 2},
     'idx2': {0: 'A', 1: 'B', 2: 'A', 3: 'A', 4: 'B', 5: 'A'}}
    )
    df1, df2, join_columns = create_test_data
    comparison = compare.Comparison(df1, df2, join_columns)
    df2_unq_columns = comparison.df2_unq_columns()
    assert df2_unq_columns.equals(expected_df2_unq_columns)

def test_df1_unq_rows(create_test_data: tuple):
    expected_df1_unq_rows = pd.DataFrame(
    {'idx1': {5: 4},
     'idx2': {5: 'A'},
     'fname': {5: 'Steve'},
     'lname': {5: 'Jobs'},
     'emptycol': {5: ""},
     'email': {5: 'sj@apple.com'},
     'dob': {5: pd.Timestamp('1955-02-24 00:00:00')},
     'active': {5: True}}
    )
    df1, df2, join_columns = create_test_data
    comparison = compare.Comparison(df1, df2, join_columns)
    df1_unq_rows = comparison.df1_unq_rows().fillna("")
    assert df1_unq_rows.equals(expected_df1_unq_rows)

def test_df2_unq_rows(create_test_data: tuple):
    expected_df2_unq_rows = pd.DataFrame(
    {'idx1': {6: 2},
     'idx2': {6: 'A'},
     'fname': {6: 'Albert'},
     'lname': {6: 'Einstein'},
     'emptycol': {6: ""},
     'email': {6: 'ae@hotmail.com'},
     'dob': {6: pd.Timestamp('1879-03-14 00:00:00')},
     'active': {6: ""}}
    )
    df1, df2, join_columns = create_test_data
    comparison = compare.Comparison(df1, df2, join_columns)
    df2_unq_rows = comparison.df2_unq_rows().fillna("")
    assert df2_unq_rows.equals(expected_df2_unq_rows)

def test_intersect_columns(create_test_data: tuple):
    expected_intersect_columns = ['idx1', 'idx2', 'fname', 'lname', 'emptycol', 'email', 'dob', 'active']
    df1, df2, join_columns = create_test_data
    comparison = compare.Comparison(df1, df2, join_columns)
    intersect_columns = comparison.intersect_columns()
    assert intersect_columns == expected_intersect_columns

def test_intersect_rows(create_test_data: tuple):
    expected_intersect_rows = pd.DataFrame({
        'idx1': {0: 1, 1: 1, 2: 2, 3: 3, 4: 3},
        'idx2': {0: 'A', 1: 'B', 2: 'A', 3: 'A', 4: 'B'},
        'fname_df1': {0: 'Nikola',
        1: 'Nikola',
        2: 'Albert',
        3: 'Stephen',
        4: 'Stephen'},
        'lname_df1': {0: 'Tesla',
        1: 'Tesla',
        2: 'Einstein',
        3: 'Hawking',
        4: 'Hawking'},
        'emptycol_df1': {0: '', 1: '', 2: '', 3: '', 4: ''},
        'email_df1': {0: 'em@tesla.com',
        1: 'em@spacex.com',
        2: 'ae@gmail.com',
        3: 'sh@cam.uk',
        4: ''},
        'dob_df1': {0: pd.Timestamp('1856-07-10 00:00:00'),
        1: pd.Timestamp('1856-07-10 00:00:00'),
        2: pd.Timestamp('1879-03-14 00:00:00'),
        3: pd.Timestamp('1942-01-08 00:00:00'),
        4: pd.Timestamp('1942-01-08 00:00:00')},
        'active_df1': {0: True, 1: False, 2: True, 3: True, 4: False},
        'fname_df2': {0: 'Nick', 1: 'Nick', 2: 'Albert', 3: 'Stephen', 4: 'Stephen'},
        'lname_df2': {0: 'Tesla',
        1: 'Tesla',
        2: 'Einstein',
        3: 'Hawking',
        4: 'Hawking'},
        'emptycol_df2': {0: '', 1: '', 2: '', 3: '', 4: ''},
        'email_df2': {0: 'em@tesla.com',
        1: 'em@spacex.com',
        2: 'ae@gmail.com',
        3: 'sh@cam.uk',
        4: ''},
        'dob_df2': {0: pd.Timestamp('1856-07-10 00:00:00'),
        1: pd.Timestamp('2000-01-01 00:00:00'),
        2: pd.Timestamp('1879-03-14 00:00:00'),
        3: pd.Timestamp('1942-03-08 00:00:00'),
        4: pd.Timestamp('1942-01-08 00:00:00')},
        'active_df2': {0: True, 1: False, 2: True, 3: True, 4: False},
        '_merge': {0: 'both', 1: 'both', 2: 'both', 3: 'both', 4: 'both'},
        'fname_match': {0: False, 1: False, 2: True, 3: True, 4: True},
        'lname_match': {0: True, 1: True, 2: True, 3: True, 4: True},
        'emptycol_match': {0: True, 1: True, 2: True, 3: True, 4: True},
        'email_match': {0: True, 1: True, 2: True, 3: True, 4: True},
        'dob_match': {0: True, 1: False, 2: True, 3: False, 4: True},
        'active_match': {0: True, 1: True, 2: True, 3: True, 4: True}
    })
    df1, df2, join_columns = create_test_data
    comparison = compare.Comparison(df1, df2, join_columns)
    intersect_rows = comparison.intersect_rows().fillna("")
    dtime_cols = intersect_rows.select_dtypes(include=['datetime'])
    intersect_rows[dtime_cols.columns] = dtime_cols.fillna(pd.to_datetime('2000-01-01'))
    intersect_rows["_merge"] = intersect_rows["_merge"].astype("object")
    assert intersect_rows.equals(expected_intersect_rows)