"""
XLSX（Excel）写入器 —— 仅 TXT 输入可用，通过"错误报文一键转换"按钮触发。

写出三列：timestamp / id / data，首行冻结，启用自动筛选。
"""

import pandas as pd
from openpyxl.styles import Alignment, Font
from src.converters.base import FrameRecord


class XLSXWriter:
    """XLSX 文件写入器。

    通过专用按钮"错误报文一键转换"触发，不参与常规格式转换流程。
    """

    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        """将 FrameRecord 列表写入 .xlsx 文件。

        生成三列：timestamp（浮点秒）、id（0x 前缀十六进制）、
        data（空格分隔大写十六进制字节）。首行冻结，启用自动筛选。

        Args:
            records: FrameRecord 列表
            path: 输出 .xlsx 文件路径

        Raises:
            ValueError: records 为空时
        """
        if not records:
            raise ValueError("No records to write to XLSX")

        rows = [
            {
                "timestamp": f"{r.timestamp:.3f}",
                "id": hex(r.arbitration_id),
                "data": " ".join(f"{b:02X}" for b in r.data),
            }
            for r in records
        ]
        df = pd.DataFrame(rows)

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="CAN")
            ws = writer.sheets["CAN"]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = f"A1:C{len(df)}"
            # 所有单元格：居中 + 文本格式（表头加粗）
            center = Alignment(horizontal="center")
            bold = Font(bold=True)
            for row in ws.iter_rows(min_row=1, max_row=len(df) + 1, min_col=1, max_col=3):
                for cell in row:
                    cell.alignment = center
                    cell.number_format = "@"
                    if cell.row == 1:
                        cell.font = bold
            _autofit_columns(ws)


def _autofit_columns(ws) -> None:
    """根据内容自动调整列宽（额外留 2 个字符间距）。"""
    for col_cells in ws.columns:
        max_len = 0
        col_letter = col_cells[0].column_letter
        for cell in col_cells:
            val = str(cell.value or "")
            # CJK 字符按双宽度计算
            cell_len = sum(2 if ord(c) > 127 else 1 for c in val)
            max_len = max(max_len, cell_len)
        ws.column_dimensions[col_letter].width = max_len + 2
