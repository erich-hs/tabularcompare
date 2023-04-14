import os
import math
import pandas as pd
from typing import Union
from datacompy import Compare
from ordered_set import OrderedSet

class Comparison:
    '''
    A tool for comparing two pandas DataFrames and reporting differences.

    Args:
        df1 (pd.DataFrame): The first DataFrame to compare.
        df2 (pd.DataFrame): The second DataFrame to compare.
        join_columns (Union[list, str], optional): The column(s) to use for joining the DataFrames.
            If not specified, will perform a comparison on DataFrames indices.
        ignore_columns (Union[list, str], optional): The column(s) to ignore in the comparison.
        on_index (bool, optional): If True, the DataFrames will be joined on their index instead of their columns.
        df1_name (str, optional): The name of the first DataFrame to use in the comparison report.
        df2_name (str, optional): The name of the second DataFrame to use in the comparison report.
        ignore_spaces (bool, optional): If True, leading and trailing whitespace in string columns will be ignored.
        ignore_case (bool, optional): If True, string columns will be compared case-insensitively.
        cast_column_names_lower (bool, optional): If True, column names will be converted to lowercase before comparison.

    Attributes:
        df1 (pd.DataFrame): The first DataFrame used in the comparison.
        df2 (pd.DataFrame): The second DataFrame used in the comparison.
        ignore_columns (Union[list, str]): The column(s) ignored in the comparison.
        join_columns (List[str]): The column(s) used for joining the DataFrames.
        on_index (bool): Whether the DataFrames were joined on their index.
        df1_name (str): The name of the first DataFrame used in the comparison report.
        df2_name (str): The name of the second DataFrame used in the comparison report.
        ignore_spaces (bool): Whether leading and trailing whitespace in string columns are ignored.
        ignore_case (bool): Whether string columns are compared case-insensitively.
        cast_column_names_lower (bool): Whether column names are converted to lowercase before comparison.
        df1_intersect_cols (List[str]): The columns in df1 that are also in df2.
        df2_intersect_cols (List[str]): The columns in df2 that are also in df1.
        intersect_match_cols (List[str]): The columns used for matching the DataFrames.

    Methods:
        _preprocess_int_missing(): Preprocesses the DataFrames for comparison, handling missing values and data types.
        _compare(): Compares the DataFrames and stores the differences.
        _enhanced_compare(): Performs an enhanced comparison, including row matches and detailed comparison of non-matching rows.
    '''
    def __init__(self,
                 df1: pd.DataFrame,
                 df2: pd.DataFrame,
                 join_columns: Union[list, str]=None,
                 ignore_columns: Union[list, str]=None,
                 on_index: bool=False,
                 df1_name: str="df1",
                 df2_name: str="df2",
                 ignore_spaces: bool=False,
                 ignore_case: bool=False,
                 cast_column_names_lower: bool=False) -> None:
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
        self.on_index = on_index
        self.df1_name = df1_name
        self.df2_name = df2_name
        self.ignore_spaces = ignore_spaces
        self.ignore_case = ignore_case
        self.cast_column_names_lower = cast_column_names_lower
        self.df1_intersect_cols = []
        self.df2_intersect_cols = []
        self.intersect_match_cols = []
        self._preprocess_int_missing()
        self._compare()
        self._enhanced_compare()

    def _preprocess_int_missing(self):
        '''
        Preprocess int columns with null values typecasting them to nullable integer Int64.
        '''
        intersect_columns = OrderedSet(self.df1.columns) & OrderedSet(self.df2.columns)
        if self.join_columns:
            intersect_columns = list(filter(lambda x: x not in self.join_columns, intersect_columns))
        for col in intersect_columns:
            if pd.api.types.is_float_dtype(self.df1[col]):
                # Check if int column of df1 has only integer and NaN values
                if all(x.is_integer() for x in self.df1[col] if not math.isnan(x)):
                    self.df1[col] = self.df1[col].astype('Int64')
            if pd.api.types.is_float_dtype(self.df2[col]):
                # Check if int column of df2 has only integer and NaN values
                if all(x.is_integer() for x in self.df2[col] if not math.isnan(x)):
                    self.df2[col] = self.df2[col].astype('Int64')
    
    def _compare(self) -> None:
        '''
        datacompy.Compare object.
        '''
        comparison_results = Compare(
            df1=self.df1,
            df2=self.df2,
            join_columns=self.join_columns,
            on_index=self.on_index,
            df1_name=self.df1_name,
            df2_name=self.df2_name,
            ignore_spaces=self.ignore_spaces,
            ignore_case=self.ignore_case,
            cast_column_names_lower=self.cast_column_names_lower
        )
        self.comparison_results = comparison_results
    
    def _enhanced_compare(self) -> None:
        '''
        Enhanced compare method:
        Generates a diverging subset dataframe outlining changes from df1 to df2.
        Generates a dataframe with join columns & columns present only in df1 or df2.
        Generates a dataframe with rows present only in df1 or df2.
        '''
        # Local join_columns handling when join_columns is not provided
        if self.join_columns:
            join_columns = self.join_columns
        else:
            join_columns = [""]

        # Intersect of diverging columns from df1 to df2
        for col in self.comparison_results.intersect_columns():
            if (col not in join_columns) and (sum(~self.comparison_results.intersect_rows[col + "_match"]) > 0):
                self.df1_intersect_cols.append(col + "_df1")
                self.df2_intersect_cols.append(col + "_df2")
                self.intersect_match_cols.append(col + "_match")
                # Typecasting int columns back to Int64 columns (after outer_join from datacompy.Compare)
                if pd.api.types.is_integer_dtype(self.df1[col]):
                    self.comparison_results.intersect_rows[col + "_df1"] = self.comparison_results.intersect_rows[col + "_df1"].astype('Int64')
                if pd.api.types.is_integer_dtype(self.df2[col]):
                    self.comparison_results.intersect_rows[col + "_df2"] = self.comparison_results.intersect_rows[col + "_df2"].astype('Int64')
        self.intersect_set = list(set(self.df1_intersect_cols).union(set(self.df2_intersect_cols)))
        if self.join_columns:
            self.intersect_cols = self.join_columns + self.intersect_set + self.intersect_match_cols
        else:
            self.intersect_cols = self.intersect_set + self.intersect_match_cols
        
        # Diverging subset
        diverging_subset = self.comparison_results.intersect_rows.loc[(~self.comparison_results.intersect_rows[self.intersect_match_cols]).sum(axis=1) > 0, self.intersect_cols]
        for col in self.df1_intersect_cols:
            diverging_subset[col[:-4]] = "{" + diverging_subset.loc[~diverging_subset[col[:-4] + "_match"], col].astype(str) + "} --> {" + diverging_subset.loc[~diverging_subset[col[:-4] + "_match"], col[:-4] + "_df2"].astype(str) + "}"
            diverging_subset[col[:-4]] = diverging_subset[col[:-4]].str.replace("{nan}", "{}")
            diverging_subset[col[:-4]] = diverging_subset[col[:-4]].str.replace("<NA>", "")
        if self.join_columns:
            self.diverging_subset_df = diverging_subset[join_columns + [col[:-4] for col in self.df1_intersect_cols]]
        else:
            self.diverging_subset_df = diverging_subset[[col[:-4] for col in self.df1_intersect_cols]]            

        # Unique columns and rows
        if self.join_columns:
            self.df1_unq_columns_df = self.df1[self.join_columns + list(self.comparison_results.df1_unq_columns())]
            self.df2_unq_columns_df = self.df2[self.join_columns + list(self.comparison_results.df2_unq_columns())]
        else:
            self.df1_unq_columns_df = self.df1[list(self.comparison_results.df1_unq_columns())]
            self.df2_unq_columns_df = self.df2[list(self.comparison_results.df2_unq_columns())]
        self.df1_unq_rows_df = self.comparison_results.df1_unq_rows
        self.df2_unq_rows_df = self.comparison_results.df2_unq_rows

    def report(self) -> str:
        return self.comparison_results.report()

    def diverging_subset(self) -> pd.DataFrame:
        return self.diverging_subset_df

    def df1_unq_columns(self) -> pd.DataFrame:
        return self.df1_unq_columns_df

    def df2_unq_columns(self) -> pd.DataFrame:
        return self.df2_unq_columns_df

    def df1_unq_rows(self) -> pd.DataFrame:
        return self.df1_unq_rows_df

    def df2_unq_rows(self) -> pd.DataFrame:
        return self.df2_unq_rows_df
    
    def report_to_txt(self,
                      file_name: str=None,
                      file_location: str=".") -> None:
        file_path = os.path.join(file_location, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.comparison_results.report())

    def deltas_to_excel(self,
                        file_name: str=None,
                        file_location: str=".",
                        write_originals: bool=False) -> None:
        file_path = os.path.join(file_location, file_name)
        with pd.ExcelWriter(file_path) as writer:
            if self.join_columns:
                join_length = len(self.join_columns)
                index=False
            else:
                join_length = 0
                index=True
            if write_originals:
                self.df1.to_excel(writer, sheet_name=f"{self.df1_name}"[:31], index=index)
                self.df2.to_excel(writer, sheet_name=f"{self.df2_name}"[:31], index=index)
            self.diverging_subset_df.to_excel(writer, sheet_name="Changes", index=index)
            if self.df1_unq_columns_df.shape[1] > join_length:
                self.df1_unq_columns_df.to_excel(writer, sheet_name=f"{self.df1_name}_unqCols"[:31], index=index)
            if self.df2_unq_columns_df.shape[1] > join_length:
                self.df2_unq_columns_df.to_excel(writer, sheet_name=f"{self.df2_name}_unqCols"[:31], index=index)
            if self.df1_unq_rows_df.shape[0] > 0:
                self.df1_unq_rows_df.to_excel(writer, sheet_name=f"{self.df1_name}_unqRows"[:31], index=index)
            if self.df2_unq_rows_df.shape[0] > 0:
                self.df2_unq_rows_df.to_excel(writer, sheet_name=f"{self.df2_name}_unqRows"[:31], index=index)