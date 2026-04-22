# Environment-based color translation and mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ColorMap:
    black: str
    dark_blue: str
    dark_green: str
    dark_aqua: str
    dark_red: str
    dark_purple: str
    gold: str
    gray: str
    dark_gray: str
    blue: str
    green: str
    aqua: str
    red: str
    light_purple: str
    yellow: str
    white: str
    reset: str
    bold: str
    italic: str

    def as_dict(self):
        """Convert dataclass to dict with <tags> as keys."""
        return {
            f"<{field}>": getattr(self, field)
            for field in self.__dataclass_fields__
        }


MC_COLOR_MAP = ColorMap(
    black="§0",
    dark_blue="§1",
    dark_green="§2",
    dark_aqua="§3",
    dark_red="§4",
    dark_purple="§5",
    gold="§6",
    gray="§7",
    dark_gray="§8",
    blue="§9",
    green="§a",
    aqua="§b",
    red="§c",
    light_purple="§d",
    yellow="§e",
    white="§f",
    reset="§r",
    bold="§l",
    italic="§o"
)

ASCII_COLOR_MAP = ColorMap(
    black="\033[30m",
    dark_blue="\033[34m",
    dark_green="\033[32m",
    dark_aqua="\033[36m",
    dark_red="\033[31m",
    dark_purple="\033[35m",
    gold="\033[33m",
    gray="\033[37m",
    dark_gray="\033[90m",
    blue="\033[94m",
    green="\033[92m",
    aqua="\033[96m",
    red="\033[91m",
    light_purple="\033[95m",
    yellow="\033[93m",
    white="\033[97m",
    reset="\033[0m",
    bold="\033[1m",
    italic="\033[3m"
)
