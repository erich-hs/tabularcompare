import os
import math
import warnings
import pandas as pd
from typing import Union
from datacompy import Compare
from ordered_set import OrderedSet
from pretty_html_table import build_table


class Comparison:
    """
    Enhanced Comparison class built on top of datacompy.Compare for comparing two pandas DataFrames and reporting differences.

    Args:
        df1 (pd.DataFrame): The first DataFrame to compare.
        df2 (pd.DataFrame): The second DataFrame to compare.
        join_columns (Union[list, str], optional): The column(s) to use for joining the DataFrames.
            If not specified, will perform a comparison on DataFrames indices.
        ignore_columns (Union[list, str], optional): The column(s) to ignore from df1 and df2 in the comparison.
        on_index (bool, optional): If True, the DataFrames will be joined on their index instead of their columns.
        df1_name (str, optional): The name of the first DataFrame to use in the comparison report.
        df2_name (str, optional): The name of the second DataFrame to use in the comparison report.
        ignore_spaces (bool, optional): If True, leading and trailing whitespace in string columns will be ignored.
        ignore_case (bool, optional): If True, string columns will be compared case-insensitively.
        abs_tol (float, optional): Absolute tolerance between two numeric values.
        rel_tol (float, optional): Relative tolerance between two numeric values.
        cast_column_names_lower (bool, optional): If True, column names will be converted to lowercase before comparison.
        encoding (str, optional): Encoding to parse txt and HTML reports. Default = "utf-8".

    Attributes:
        df1 (pd.DataFrame): The first DataFrame used in the comparison.
        df2 (pd.DataFrame): The second DataFrame used in the comparison.
        ignore_columns (Union[list, str]): The column(s) ignored in the comparison.
        join_columns (List[str]): The column(s) used for joining the DataFrames.
        df1_name (str): The name of the first DataFrame used in the comparison report.
        df2_name (str): The name of the second DataFrame used in the comparison report.
        encoding (str): ENcoding used to parse txt and HTML reports.

    Methods:
        report: Returns datacompy.Compare report.
        diverging_subset: Returns a pandas DataFrame with the complete diverging subset of df1 and df2, showing only deltas.
            Formatting follows the rule: {df1} --> {df2}.
        df1_unq_columns: Returns a pandas DataFrame with join_columns (or index, if join_columns = None) and columns present only in df1.
        df2_unq_columns: Returns a pandas DataFrame with join_columns (or index, if join_columns = None) and columns present only in df2.
        df1_unq_rows: Returns a pandas DataFrame with the df1 subset that is unique to df1.
        df2_unq_rows: Returns a pandas DataFrame with the df2 subset that is unique to df2.
        intersect_columns: Returns a set of columns present in both df1 and df2.
        report_to_txt: Saves datacompy.Compare report in txt.
        report_to_html: Saves datacompy.Compare report in HTML.
        report_to_xlsx: Saves a .xlsx report with the diverging subset, unique columns, and unique rows to df1 and df2.
    """

    # TODO:
    # 1. Handle case when df1 has column completely missing and df2 doesn't.
    #   TypeError: boolean value of NA is ambiguous

    def __init__(
        self,
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        join_columns: Union[list, str] = None,
        ignore_columns: Union[list, str] = None,
        on_index: bool = False,
        abs_tol: int = 0,
        rel_tol: int = 0,
        df1_name: str = "df1",
        df2_name: str = "df2",
        ignore_spaces: bool = False,
        ignore_case: bool = False,
        cast_column_names_lower: bool = False,
        encoding: str = "utf-8",
    ) -> None:
        self.df1 = df1
        self.df2 = df2
        self.ignore_columns = ignore_columns
        if self.ignore_columns:
            if isinstance(ignore_columns, str):
                self.ignore_columns = [ignore_columns]
            try:
                self.df1.drop(columns=self.ignore_columns, inplace=True)
                self.df2.drop(columns=self.ignore_columns, inplace=True)
            except KeyError:
                pass
        if isinstance(join_columns, str):
            self.join_columns = [join_columns]
        else:
            self.join_columns = join_columns
        self.df1_name = df1_name
        self.df2_name = df2_name
        self.encoding = encoding
        self._on_index = on_index
        self._abs_tol = abs_tol
        self._rel_tol = rel_tol
        self._ignore_spaces = ignore_spaces
        self._ignore_case = ignore_case
        self._cast_column_names_lower = cast_column_names_lower
        self._df1_intersect_cols = []
        self._df2_intersect_cols = []
        self._intersect_match_cols = []
        self._handle_join()
        self._preprocess_int_missing()
        self._compare()
        self._enhanced_compare()
    
    # join_columns and on_index handling
    def _handle_join(self):
        if self.join_columns is None and not self._on_index:
            warnings.warn("The join_columns parameter was not provided. Performing join on DataFrame indices. Set on_index=True to silence this warning.")
            self._on_index = True

    def _preprocess_int_missing(self):
        """
        Preprocess int columns with null values typecasting them to nullable integer Int64.
        """
        intersect_columns = OrderedSet(self.df1.columns) & OrderedSet(self.df2.columns)
        if self.join_columns:
            intersect_columns = list(
                filter(lambda x: x not in self.join_columns, intersect_columns)
            )
        for col in intersect_columns:
            if pd.api.types.is_float_dtype(self.df1[col]):
                # Check if int column of df1 has only integer and NaN values
                if all(x.is_integer() for x in self.df1[col] if not math.isnan(x)):
                    self.df1[col] = self.df1[col].astype("Int64")
            if pd.api.types.is_float_dtype(self.df2[col]):
                # Check if int column of df2 has only integer and NaN values
                if all(x.is_integer() for x in self.df2[col] if not math.isnan(x)):
                    self.df2[col] = self.df2[col].astype("Int64")

    def _compare(self) -> None:
        """
        datacompy.Compare object.
        """
        comparison_results = Compare(
            df1=self.df1,
            df2=self.df2,
            join_columns=self.join_columns,
            on_index=self._on_index,
            abs_tol=self._abs_tol,
            rel_tol=self._rel_tol,
            df1_name=self.df1_name,
            df2_name=self.df2_name,
            ignore_spaces=self._ignore_spaces,
            ignore_case=self._ignore_case,
            cast_column_names_lower=self._cast_column_names_lower,
        )
        self._comparison_results = comparison_results

    def _enhanced_compare(self) -> None:
        """
        Enhanced compare method:
        Generates a diverging subset dataframe outlining changes from df1 to df2.
        Generates a dataframe with join columns & columns present only in df1 or df2.
        Generates a dataframe with rows present only in df1 or df2.
        """
        # Local join_columns handling when join_columns is not provided
        if self.join_columns:
            join_columns = self.join_columns
        else:
            join_columns = [""]

        # Intersect of diverging columns from df1 to df2
        for col in self._comparison_results.intersect_columns():
            if (col not in join_columns) and (
                sum(~self._comparison_results.intersect_rows[col + "_match"]) > 0
            ):
                self._df1_intersect_cols.append(col + "_df1")
                self._df2_intersect_cols.append(col + "_df2")
                self._intersect_match_cols.append(col + "_match")
                # Typecasting int columns back to Int64 columns (after outer_join from datacompy.Compare)
                if pd.api.types.is_integer_dtype(self.df1[col]):
                    self._comparison_results.intersect_rows[
                        col + "_df1"
                    ] = self._comparison_results.intersect_rows[col + "_df1"].astype(
                        "Int64"
                    )
                if pd.api.types.is_integer_dtype(self.df2[col]):
                    self._comparison_results.intersect_rows[
                        col + "_df2"
                    ] = self._comparison_results.intersect_rows[col + "_df2"].astype(
                        "Int64"
                    )
        self._intersect_set = list(
            set(self._df1_intersect_cols).union(set(self._df2_intersect_cols))
        )
        if self.join_columns:
            self._intersect_cols = (
                self.join_columns + self._intersect_set + self._intersect_match_cols
            )
        else:
            self._intersect_cols = self._intersect_set + self._intersect_match_cols

        # Diverging subset
        diverging_subset = self._comparison_results.intersect_rows.loc[
            (~self._comparison_results.intersect_rows[self._intersect_match_cols]).sum(
                axis=1
            )
            > 0,
            self._intersect_cols,
        ]
        for col in self._df1_intersect_cols:
            diverging_subset[col[:-4]] = (
                "{"
                + diverging_subset.loc[
                    ~diverging_subset[col[:-4] + "_match"], col
                ].astype(str)
                + "} --> {"
                + diverging_subset.loc[
                    ~diverging_subset[col[:-4] + "_match"], col[:-4] + "_df2"
                ].astype(str)
                + "}"
            )
            diverging_subset[col[:-4]] = diverging_subset[col[:-4]].str.replace(
                "{nan}", "{}", regex=False
            )
            diverging_subset[col[:-4]] = diverging_subset[col[:-4]].str.replace(
                "<NA>", "", regex=False
            )
        if self.join_columns:
            self._diverging_subset_df = diverging_subset[
                join_columns + [col[:-4] for col in self._df1_intersect_cols]
            ]
        else:
            self._diverging_subset_df = diverging_subset[
                [col[:-4] for col in self._df1_intersect_cols]
            ]

        # Unique columns and rows
        if self.join_columns:
            self._df1_unq_columns_df = self.df1[
                self.join_columns + list(self._comparison_results.df1_unq_columns())
            ]
            self._df2_unq_columns_df = self.df2[
                self.join_columns + list(self._comparison_results.df2_unq_columns())
            ]
        else:
            self._df1_unq_columns_df = self.df1[
                list(self._comparison_results.df1_unq_columns())
            ]
            self._df2_unq_columns_df = self.df2[
                list(self._comparison_results.df2_unq_columns())
            ]
        self._df1_unq_rows_df = self._comparison_results.df1_unq_rows
        self._df2_unq_rows_df = self._comparison_results.df2_unq_rows

    def report(self, sample_count=10, column_count=10) -> str:
        """
        Returns datacompy.Compare report.
        Args:
            sample_count (int): The number of sample records to return in the report. Default = 10.
            column_count (int): The number of columns to display in the sample records output. Default = 10.
        """
        return self._comparison_results.report(
            sample_count=sample_count, column_count=column_count
        )

    def diverging_subset(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with the complete diverging subset of df1 and df2, showing only deltas.
        Formatting follows the rule: {df1} --> {df2}.
        """
        return self._diverging_subset_df

    def df1_unq_columns(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with join_columns (or index, if join_columns = None) and columns present only in df1.
        """
        return self._df1_unq_columns_df

    def df2_unq_columns(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with join_columns (or index, if join_columns = None) and columns present only in df2.
        """
        return self._df2_unq_columns_df

    def df1_unq_rows(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with the df1 subset that is unique to df1.
        """
        return self._df1_unq_rows_df

    def df2_unq_rows(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with the df2 subset that is unique to df2.
        """
        return self._df2_unq_rows_df

    def intersect_columns(self) -> OrderedSet:
        """
        Returns a set of columns present in both df1 and df2.
        """
        return OrderedSet(self.df1.columns) & OrderedSet(self.df2.columns)
    
    def intersect_rows(self) -> pd.DataFrame:
        """
        Returns a pandas DataFrame with the subset of matching rows between df1 and df2.
        """
        return self._comparison_results.intersect_rows

    def report_to_txt(
        self,
        file_name: str,
        sample_count: int = 10,
        column_count: int = 10,
        file_location: str = ".",
    ) -> None:
        """
        Saves datacompy.Compare report in txt.
        Args:
            sample_count (int): The number of sample records to return in the report. Default = 10.
            column_count (int): The number of columns to display in the sample records output. Default = 10.
            file_name (str): File name. Can optionally be a file path relative to the current directory.
            file_location (str, optional): Destination file path. Default = current directory '.'.
        """
        if not file_name.endswith(".txt"):
            file_name += ".txt"
        file_path = os.path.join(file_location, file_name)
        with open(file_path, "w", encoding=self.encoding) as file:
            file.write(self._comparison_results.report(sample_count, column_count))

    def report_to_html(
        self,
        file_name: str,
        max_diverging_records: int = 100,
        max_diverging_columns: int = 10,
        sample_count: int = 10,
        column_count: int = 10,
        file_location: str = ".",
    ) -> None:
        """
        Saves datacompy.Compare report in HTML.
        Args:
            max_diverging_records (int): The maximum number of records to render the diverging subset table. Default = 100.
            max_diverging_columns (int): The maximum number of columns to render the diverging subset table. Default = 10.
            sample_count (int): The number of sample records to return in the report. Default = 10.
            column_count (int): The number of columns to display in the sample records output. Default = 10.
            file_name (str): File name. Can optionally be a file path relative to the current directory.
            file_location (str, optional): Destination file path. Default = current directory '.'.
        """
        if not file_name.endswith(".html"):
            file_name += ".html"
        file_path = os.path.join(file_location, file_name)
        col_widths = []
        for col in self._diverging_subset_df.columns:
            col_max_length = self._diverging_subset_df[col].astype(str).str.len().max()
            col_width = "auto" if col_max_length < 25 else "160px"
            col_widths.append(col_width)
        html_table_rows = self._diverging_subset_df.index[:max_diverging_records]
        html_table_cols = self._diverging_subset_df.columns[:max_diverging_columns]
        html_table = self._diverging_subset_df.loc[html_table_rows, html_table_cols]
        html_table = build_table(
            html_table,
            "grey_dark",
            font_size="12px",
            font_family="Monospace",
            width_dict=col_widths,
        )
        html_report = (
            self._comparison_results.report(sample_count, column_count)
            .replace("\n", "<br>")
            .replace(" ", "&nbsp;")
        )
        html_report = f"<pre>{html_report}</pre>"
        html_report = (
            '<p style="font-size: 12.5px; font-family: Monospace;">TabularCompare Diverging Subset</p>'
            + html_table
            + html_report
        )
        with open(file_path, "w", encoding=self.encoding) as file:
            file.write(html_report)

    def report_to_xlsx(
        self,
        file_name: str = None,
        file_location: str = ".",
        write_originals: bool = False,
    ) -> None:
        """
        Saves a .xlsx report with the diverging subset, unique columns, and unique rows to df1 and df2.
        Optionally writes the original dataframes in independent tabs.
        Args:
            file_name (str): File name. Can optionally be a file path relative to the current directory.
            file_location (str, optional): Destination file path. Default = current directory '.'.
            write_originals (bool, optional): Flag to write original dataframes in independent tabs when True. Default = False.
        """
        if not file_name.endswith(".xlsx"):
            file_name += ".xlsx"
        file_path = os.path.join(file_location, file_name)
        with pd.ExcelWriter(file_path) as writer:
            if self.join_columns:
                join_length = len(self.join_columns)
                index = False
            else:
                join_length = 0
                index = True
            if write_originals:
                self.df1.to_excel(
                    writer, sheet_name=f"{self.df1_name}"[:31], index=index
                )
                self.df2.to_excel(
                    writer, sheet_name=f"{self.df2_name}"[:31], index=index
                )
            self._diverging_subset_df.to_excel(
                writer, sheet_name="Changes", index=index
            )
            if self._df1_unq_columns_df.shape[1] > join_length:
                self._df1_unq_columns_df.to_excel(
                    writer, sheet_name=f"{self.df1_name}_unqCols"[:31], index=index
                )
            if self._df2_unq_columns_df.shape[1] > join_length:
                self._df2_unq_columns_df.to_excel(
                    writer, sheet_name=f"{self.df2_name}_unqCols"[:31], index=index
                )
            if self._df1_unq_rows_df.shape[0] > 0:
                self._df1_unq_rows_df.to_excel(
                    writer, sheet_name=f"{self.df1_name}_unqRows"[:31], index=index
                )
            if self._df2_unq_rows_df.shape[0] > 0:
                self._df2_unq_rows_df.to_excel(
                    writer, sheet_name=f"{self.df2_name}_unqRows"[:31], index=index
                )
