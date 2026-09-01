from dataclasses import dataclass, field


@dataclass
class LayoutSignals:
    """
    Measurable visual/layout characteristics.

    These are signals, not semantic classifications.
    """

    column_index: int | None = None

    left_x: float | None = None
    right_x: float | None = None

    is_left_aligned: bool = False
    is_right_aligned: bool = False

    is_list_like: bool = False
    is_table_like: bool = False

    indentation_level: int = 0

    repeated_x_position: bool = False