"""Reusable tools for ADK Agents"""
import gspread


class GoogleSheetClient:
    def __init__(self, sheet_id: str):
        self.gc = gspread.service_account()
        self.spreadsheet_id = sheet_id
        self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
        self.worksheet = self.spreadsheet.get_worksheet_by_id(0)
        self.fields = None

    def _get_fields(self) -> None:
        self.fields = self.worksheet.row_values(1)

    def append_rows(self, rows: dict | list[dict], table_range: str) -> None:
        if not self.fields:
            self._get_fields()
        if isinstance(rows, dict):
            rows = [rows]

        append_rows = []
        for row in rows:
            append_row = [row.get(field) for field in self.fields]
            append_rows.append(append_row)
        self.worksheet.append_rows(append_rows, table_range=table_range)
        return


def financial_update(sheet_id: str, new_data_row: dict) -> str:
    """This function insert the data as as new row into the financial data sheet.

    Args:
        sheet_id (str): the google sheet id of the financial data sheet
        new_data_row (dict): the new data to append into the sheet

    Returns:
        str
    """
    gs_client = GoogleSheetClient(sheet_id)
    gs_client.append_rows(new_data_row, table_range="1:1")
    return "success"
