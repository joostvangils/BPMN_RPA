import pickle

import win32com
import win32com.client


# The BPMN-RPA Excel module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA Excel module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


class Excel:

    def __init__(self, path: str, visible: bool = False, read_only: bool = False, update_links: bool = False, format: str = "xlsx"):
        """
        Open an Excel file and initialize the Excel class for user by other functions.
        :param path: The full path to the Excel file.
        :param visible: Optional. Whether the Excel file should be visible or not.
        :param read_only: Optional. Whether the Excel file should be opened in read-only mode.
        :param update_links: Optional. Whether the Excel file should update links.
        :param format: Optional. The format of the Excel file.
        """
        self.Visible = visible
        self.excel = None
        self.path = path
        self.read_only = read_only
        self.update_links = update_links
        self.format = format
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to Excel.
        :return: None
        """
        self.excel = win32com.client.Dispatch("Excel.Application")
        self.excel.Visible = self.Visible
        self.excel.DisplayAlerts = False
        self.excel.Workbooks.Open(self.path, ReadOnly=self.read_only, UpdateLinks=self.update_links, Format=self.format)

    def __is_picklable__(self, obj: any) -> bool:
        """
        Internal function to determine if the object is pickable.
        :param obj: The object to check.
        :return: True or False
        """
        try:
            pickle.dumps(obj)
            return True
        except Exception as e:
            return False

    def __getstate__(self):
        """
        Internal function for serialization
        """
        self.close(save_changes=True)
        state = self.__dict__.copy()
        for key, val in state.items():
            if not self.__is_picklable__(val):
                state[key] = str(val)
        return state

    def __setstate__(self, state):
        """
        Internal function for deserialization
        :param state: The state to set to the 'self' object of the class
        """
        self.__dict__.update(state)
        self.__connect__()

    def close(self, save_changes: bool = False):
        """
        Close an Excel file.
        :param save_changes: Optional. Whether to save changes to the Excel file.
        :return: None
        """
        self.excel.Workbooks.Close(SaveChanges=save_changes)
        self.excel.Quit()

    def get_cell_value(self, sheet: str, cell: str):
        """
        Get the value of a cell in an Excel file.
        :param sheet: The name of the sheet.
        :param cell: The cell to get the value of.
        :return: The value of the cell.
        """
        return self.excel.Worksheets(sheet).Range(cell).Value

    def set_cell_value(self, sheet: str, cell: str, value: str):
        """
        Set the value of a cell in an Excel file.
        :param sheet: The name of the sheet.
        :param cell: The cell to set the value of.
        :param value: The value to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Range(cell).Value = value

    def get_row_values(self, sheet: str, row: int):
        """
        Get the values of a row in an Excel file.
        :param sheet: The name of the sheet.
        :param row: The row to get the values of.
        :return: The values of the row.
        """
        return self.excel.Worksheets(sheet).Rows(row).Value

    def set_row_values(self, sheet: str, row: int, values: list):
        """
        Set the values of a row in an Excel file.
        :param sheet: The name of the sheet.
        :param row: The row to set the values of.
        :param values: The values to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Rows(row).Value = values

    def get_column_values(self, sheet: str, column: int):
        """
        Get the values of a column in an Excel file.
        :param sheet: The name of the sheet.
        :param column: The column to get the values of.
        :return: The values of the column.
        """
        return self.excel.Worksheets(sheet).Columns(column).Value

    def set_column_values(self, sheet: str, column: int, values: list):
        """
        Set the values of a column in an Excel file.
        :param sheet: The name of the sheet.
        :param column: The column to set the values of.
        :param values: The values to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Columns(column).Value = values

    def get_sheet_values(self, sheet: str):
        """
        Get the values of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :return: The values of the sheet.
        """
        return self.excel.Worksheets(sheet).Value

    def set_sheet_values(self, sheet: str, values: list):
        """
        Set the values of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param values: The values to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Value = values

    def get_sheet_names(self):
        """
        Get the names of the sheets in an Excel file.
        :return: The names of the sheets.
        """
        return self.excel.Worksheets.Names

    def get_sheet_name(self, sheet: str):
        """
        Get the name of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :return: The name of the sheet.
        """
        return self.excel.Worksheets(sheet).Name

    def set_sheet_name(self, sheet: str, name: str):
        """
        Set the name of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param name: The name to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Name = name

    def get_sheet_index(self, sheet: str):
        """
        Get the index of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :return: The index of the sheet.
        """
        return self.excel.Worksheets(sheet).Index

    def set_sheet_index(self, sheet: str, index: int):
        """
        Set the index of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param index: The index to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Index = index

    def get_sheet_visible(self, sheet: str):
        """
        Get the visibility of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :return: The visibility of the sheet.
        """
        return self.excel.Worksheets(sheet).Visible

    def set_sheet_visible(self, sheet: str, visible: bool):
        """
        Set the visibility of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param visible: The visibility to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Visible = visible

    def get_sheet_protected(self, sheet: str):
        """
        Get the protection of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :return: The protection of the sheet.
        """
        return self.excel.Worksheets(sheet).ProtectContents

    def set_sheet_protected(self, sheet: str, protected: bool):
        """
        Set the protection of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param protected: The protection to set.
        :return: None
        """
        self.excel.Worksheets(sheet).ProtectContents = protected

    def get_sheet_password(self, sheet: str):
        """
        Get the password of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :return: The password of the sheet.
        """
        return self.excel.Worksheets(sheet).Password

    def set_sheet_password(self, sheet: str, password: str):
        """
        Set the password of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param password: The password to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Password = password

    def get_sheet_password_protected(self, sheet: str):
        """
        Get the password protection of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :return: The password protection of the sheet.
        """
        return self.excel.Worksheets(sheet).ProtectDrawingObjects

    def set_sheet_password_protected(self, sheet: str, protected: bool):
        """
        Set the password protection of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param protected: The password protection to set.
        :return: None
        """
        self.excel.Worksheets(sheet).ProtectDrawingObjects = protected

    def add_new_sheet(self, sheet: str):
        """
        Add a new sheet to an Excel file.
        :param sheet: The name of the sheet.
        :return: None
        """
        self.excel.Worksheets.Add().Name = sheet

    def delete_sheet(self, sheet: str):
        """
        Delete a sheet from an Excel file.
        :param sheet: The name of the sheet.
        :return: None
        """
        self.excel.Worksheets(sheet).Delete()

    def get_sheet_range(self, sheet: str, range: str):
        """
        Get a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to get.
        :return: The range.
        """
        return self.excel.Worksheets(sheet).Range(range)

    def get_sheet_range_value(self, sheet: str, range: str):
        """
        Get the value of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to get the value of.
        :return: The value of the range.
        """
        return self.excel.Worksheets(sheet).Range(range).Value

    def set_sheet_range_value(self, sheet: str, range: str, value: str):
        """
        Set the value of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to set the value of.
        :param value: The value to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Range(range).Value = value

    def get_sheet_range_address(self, sheet: str, range: str):
        """
        Get the address of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to get the address of.
        :return: The address of the range.
        """
        return self.excel.Worksheets(sheet).Range(range).Address

    def get_sheet_range_address_local(self, sheet: str, range: str):
        """
        Get the local address of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to get the local address of.
        :return: The local address of the range.
        """
        return self.excel.Worksheets(sheet).Range(range).AddressLocal

    def get_sheet_range_address_relative(self, sheet: str, range: str):
        """
        Get the relative address of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to get the relative address of.
        :return: The relative address of the range.
        """
        return self.excel.Worksheets(sheet).Range(range).AddressRelative

    def get_first_free_row(self, sheet: str):
        """
        Get the first free row of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :return: The first free row.
        """
        return self.excel.Worksheets(sheet).UsedRange.Rows.Count + 1

    def get_first_free_column(self, sheet: str):
        """
        Get the first free column of a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :return: The first free column.
        """
        return self.excel.Worksheets(sheet).UsedRange.Columns.Count + 1

    def get_sheet_range_formula(self, sheet: str, range: str):
        """
        Get the formula of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to get the formula of.
        :return: The formula of the range.
        """
        return self.excel.Worksheets(sheet).Range(range).Formula

    def set_sheet_range_formula(self, sheet: str, range: str, formula: str):
        """
        Set the formula of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to set the formula of.
        :param formula: The formula to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Range(range).Formula = formula

    def get_sheet_range_formula_local(self, sheet: str, range: str):
        """
        Get the local formula of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to get the local formula of.
        :return: The local formula of the range.
        """
        return self.excel.Worksheets(sheet).Range(range).FormulaLocal

    def set_sheet_range_formula_local(self, sheet: str, range: str, formula: str):
        """
        Set the local formula of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to set the local formula of.
        :param formula: The local formula to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Range(range).FormulaLocal = formula

    def get_sheet_range_formula_r1c1(self, sheet: str, range: str):
        """
        Get the R1C1 formula of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to get the R1C1 formula of.
        :return: The R1C1 formula of the range.
        """
        return self.excel.Worksheets(sheet).Range(range).FormulaR1C1

    def set_sheet_range_formula_r1c1(self, sheet: str, range: str, formula: str):
        """
        Set the R1C1 formula of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to set the R1C1 formula of.
        :param formula: The R1C1 formula to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Range(range).FormulaR1C1 = formula

    def get_sheet_range_formula_local_r1c1(self, sheet: str, range: str):
        """
        Get the local R1C1 formula of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to get the local R1C1 formula of.
        :return: The local R1C1 formula of the range.
        """
        return self.excel.Worksheets(sheet).Range(range).FormulaLocalR1C1

    def set_sheet_range_formula_local_r1c1(self, sheet: str, range: str, formula: str):
        """
        Set the local R1C1 formula of a range from a sheet in an Excel file.
        :param sheet: The name of the sheet.
        :param range: The range to set the local R1C1 formula of.
        :param formula: The local R1C1 formula to set.
        :return: None
        """
        self.excel.Worksheets(sheet).Range(range).FormulaLocalR1C1 = formula

    def does_sheet_range_contain_formula(self, sheet: str, range: str):
        """
        Check if a range from a sheet in an Excel file contains a formula.
        :param sheet: The name of the sheet.
        :param range: The range to check.
        :return: True if the range contains a formula, False otherwise.
        """
        return self.excel.Worksheets(sheet).Range(range).HasFormula

    def does_sheet_has_header(self, sheet: str):
        """
        Check if a sheet in an Excel file has a header.
        :param sheet: The name of the sheet.
        :return: True if the sheet has a header, False otherwise.
        """
        return self.excel.Worksheets(sheet).HasHeader

    def set_sheet_has_header(self, sheet: str, has_header: bool):
        """
        Set if a sheet in an Excel file has a header.
        :param sheet: The name of the sheet.
        :param has_header: True if the sheet should have a header, False otherwise.
        :return: None
        """
        self.excel.Worksheets(sheet).HasHeader = has_header

    def does_sheet_has_hyperlinks(self, sheet: str):
        """
        Check if a sheet in an Excel file has hyperlinks.
        :param sheet: The name of the sheet.
        :return: True if the sheet has hyperlinks, False otherwise.
        """
        return self.excel.Worksheets(sheet).HasHyperlinks

    def does_sheet_has_merged_cells(self, sheet: str):
        """
        Check if a sheet in an Excel file has merged cells.
        :param sheet: The name of the sheet.
        :return: True if the sheet has merged cells, False otherwise.
        """
        return self.excel.Worksheets(sheet).HasMergedCells

    def does_sheet_has_pivot_table(self, sheet: str):
        """
        Check if a sheet in an Excel file has a pivot table.
        :param sheet: The name of the sheet.
        :return: True if the sheet has a pivot table, False otherwise.
        """
        return self.excel.Worksheets(sheet).HasPivotTable

    def does_sheet_has_query_table(self, sheet: str):
        """
        Check if a sheet in an Excel file has a query table.
        :param sheet: The name of the sheet.
        :return: True if the sheet has a query table, False otherwise.
        """
        return self.excel.Worksheets(sheet).HasQueryTable

    def does_sheet_has_table(self, sheet: str):
        """
        Check if a sheet in an Excel file has a table.
        :param sheet: The name of the sheet.
        :return: True if the sheet has a table, False otherwise.
        """
        return self.excel.Worksheets(sheet).HasTable

    def does_sheet_has_vba_code(self, sheet: str):
        """
        Check if a sheet in an Excel file has VBA code.
        :param sheet: The name of the sheet.
        :return: True if the sheet has VBA code, False otherwise.
        """
        return self.excel.Worksheets(sheet).HasVBACode

    def save_workbook(self):
        """
        Save the workbook.
        :return: None
        """
        self.excel.ActiveWorkbook.Save()

    def save_workbook_as(self, path: str):
        """
        Save the workbook as a new file.
        :param path: The path to save the workbook as.
        :return: None
        """
        self.excel.ActiveWorkbook.SaveAs(path)

    def close_workbook(self):
        """
        Close the workbook.
        :return: None
        """
        self.excel.ActiveWorkbook.Close()

    def table_to_range(self, sheet: str, table: str, range: str):
        """
        Copy a table to a range.
        :param sheet: The name of the sheet.
        :param table: The name of the table.
        :param range: The range to copy the table to.
        :return: None
        """
        self.excel.Worksheets(sheet).ListObjects(table).Range.Copy(self.excel.Worksheets(sheet).Range(range))

    def range_to_table(self, sheet: str, range: str, table: str):
        """
        Copy a range to a table.
        :param sheet: The name of the sheet.
        :param range: The range to copy.
        :param table: The name of the table.
        :return: None
        """
        self.excel.Worksheets(sheet).Range(range).Copy(self.excel.Worksheets(sheet).ListObjects(table).Range)

    def insert_chart_from_table(self, sheet: str, table: str, chart_type: str, chart_name: str):
        """
        Insert a chart from a table.
        :param sheet: The name of the sheet.
        :param table: The name of the table.
        :param chart_type: The type of chart to insert.
        :param chart_name: The name of the chart.
        :return: None
        """
        self.excel.Worksheets(sheet).ListObjects(table).Range.Chart.ChartType = chart_type
        self.excel.Worksheets(sheet).ListObjects(table).Range.Chart.Name = chart_name

    def insert_chart_from_range(self, sheet: str, range: str, chart_type: str, chart_name: str):
        """
        Insert a chart from a range.
        :param sheet: The name of the sheet.
        :param range: The range to insert the chart from.
        :param chart_type: The type of chart to insert.
        :param chart_name: The name of the chart.
        :return: None
        """
        self.excel.Worksheets(sheet).Range(range).Chart.ChartType = chart_type
        self.excel.Worksheets(sheet).Range(range).Chart.Name = chart_name

    def insert_chart_from_sheet(self, sheet: str, chart_type: str, chart_name: str):
        """
        Insert a chart from a sheet.
        :param sheet: The name of the sheet.
        :param chart_type: The type of chart to insert.
        :param chart_name: The name of the chart.
        :return: None
        """
        self.excel.Worksheets(sheet).Chart.ChartType = chart_type
        self.excel.Worksheets(sheet).Chart.Name = chart_name

    def insert_table_from_range(self, sheet: str, range: str, table_name: str):
        """
        Insert a table from a range.
        :param sheet: The name of the sheet.
        :param range: The range to insert the table from.
        :param table_name: The name of the table.
        :return: None
        """
        self.excel.Worksheets(sheet).Range(range).ListObject.Name = table_name

    def save_as_csv(self, path: str):
        """
        Save the workbook as a CSV file.
        :param path: The path to save the CSV file as.
        :return: None
        """
        self.excel.ActiveWorkbook.SaveAs(path, FileFormat=62)

    def save_as_pdf(self, path: str):
        """
        Save the workbook as a PDF file.
        :param path: The path to save the PDF file as.
        :return: None
        """
        self.excel.ActiveWorkbook.ExportAsFixedFormat(0, path)
