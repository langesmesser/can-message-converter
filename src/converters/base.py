"""
CAN/LIN 总线报文数据模型和转换器抽象基类。

本模块定义了整个转换系统的核心数据结构 FrameRecord（冻结数据类，作为
所有格式互转的中间表示）和 Converter 抽象基类（定义 Reader/Writer 契约）。

架构设计：所有转换器遵循"源格式 → FrameRecord 列表 → 目标格式"的模式，
每种格式只需实现 Reader（读取为 FrameRecord）和 Writer（从 FrameRecord 写出），
即可实现所有格式间的 N×M 互转。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class FrameRecord:
    """总线报文帧的中间表示，不可变（冻结数据类）。

    所有格式的读写器都以 FrameRecord 作为中转。字段设计覆盖了
    CAN 2.0、CAN FD 和 LIN 三种协议类型，缺省值均为最宽泛的安全默认值。

    Attributes:
        timestamp: 报文时间戳，单位为秒（各格式精度不同，以 float64 容纳）
        arbitration_id: 仲裁 ID（CAN 标准帧 11 位 / 扩展帧 29 位 / LIN PID）
        channel: 总线通道编号（0 起），用于区分多路总线
        is_extended: 是否为 CAN 扩展帧（29 位 ID），仅 CAN 有效
        is_lin: 是否为 LIN 报文
        is_fd: 是否为 CAN FD 帧（DLC > 8 或 EDL 标志位为真）
        dlc: Data Length Code，CAN FD 中为 0-15（9-15 对应 12/16/20/24/32/48/64 字节）
        data: 数据载荷，原始字节序列（长度由 DLC 决定，CAN FD 最大 64 字节）
        bus: 总线名称字符串（如 \"CAN1\"），用于标识物理总线
    """
    timestamp: float
    arbitration_id: int
    channel: int = 0
    is_extended: bool = False
    is_lin: bool = False
    is_fd: bool = False
    dlc: int = 8
    data: bytes = b""
    bus: str = ""


class Converter(ABC):
    """转换器抽象基类，强制子类实现 from_file（读）和 to_file（写）两个静态方法。

    采用静态方法设计，无需实例化，所有转换器作为无状态函数指针注册到 registry 中。
    """

    @staticmethod
    @abstractmethod
    def from_file(path: str) -> list[FrameRecord]:
        """从文件路径读取报文数据，返回 FrameRecord 列表。

        Args:
            path: 输入文件的绝对路径

        Returns:
            list[FrameRecord]: 解析出的帧记录列表，保持文件中的时间顺序

        Raises:
            ValueError: 文件为空或无法解析任何报文时抛出
        """

    @staticmethod
    @abstractmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        """将 FrameRecord 列表写入指定格式的文件。

        Args:
            records: 待写入的帧记录列表（非空）
            path: 输出文件的绝对路径（目录必须已存在）

        Raises:
            ValueError: records 列表为空时抛出
        """
