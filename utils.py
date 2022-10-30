from datetime import datetime as dtime
from enum import Enum


class Color(Enum):
    BLACK           = 0
    RED             = 1
    GREEN           = 2
    YELLOW          = 3
    BLUE            = 4
    MAGENTA         = 5
    CYAN            = 6
    WHITE           = 7
    RESET           = 9

    LIGHTBLACK      = 60
    LIGHTRED        = 61
    LIGHTGREEN      = 62
    LIGHTYELLOW     = 63
    LIGHTBLUE       = 64
    LIGHTMAGENTA    = 65
    LIGHTCYAN       = 66
    LIGHTWHITE      = 67


class Style(Enum):
    BRIGHT    = 1
    DIM       = 2
    NORMAL    = 22
    RESET_ALL = 0


class Double_Keys(Enum):
    ARROW_UP    = b"H"
    ARROW_DOWN  = b"P"
    ARROW_LEFT  = b"K"
    ARROW_RIGHT = b"M"
    NUM_0       = b"R" # INSERT
    NUM_1       = b"O" # END
    NUM_3       = b"Q" # PGDWN
    # NUM_5       = None
    NUM_7       = b"G" # HOME
    NUM_9       = b"I" # PGUP
    DELETE      = B"S"


def imput(ask="Num: ", type=int):
    """
    Only returns int/float.
    """
    while True:
        try: return type(input(ask))
        except ValueError: print(f'Not{" whole" if type is int else ""} number!')
        

def pad_zero(num:int|str):
    """
    Converts numbers that are smaller than 10 to have a trailing 0.
    """
    return ('0' if int(num) < 10 else '') + str(num)


def make_date(date_lis:list|dtime, sep="-"):
    """
    Turns a datetime object's date part or a list into a formated string.
    """
    if type(date_lis) is dtime:
        return f"{pad_zero(date_lis.year)}{sep}{pad_zero(date_lis.month)}{sep}{pad_zero(date_lis.day)}"
    else:
        return f"{pad_zero(date_lis[0])}{sep}{pad_zero(date_lis[1])}{sep}{pad_zero(date_lis[2])}"


def make_time(time_lis:list|dtime, sep=":", write_ms=False, ms_sep:str="."):
    """
    Turns a datetime object's time part or a list into a formated string.
    """
    if type(time_lis) is dtime:
        return f"{pad_zero(time_lis.hour)}{sep}{pad_zero(time_lis.minute)}{sep}{pad_zero(time_lis.second)}{f'{ms_sep}{time_lis.microsecond}' if write_ms else ''}"
    else:
        return f"{pad_zero(time_lis[0])}{sep}{pad_zero(time_lis[1])}{sep}{pad_zero(time_lis[2])}{f'{ms_sep}{time_lis[3]}' if write_ms else ''}"


def stylized_text(text:str, fore_color:Color, back_color=Color.RESET, style=Style.NORMAL):
    """
    Colors text fore/background.
    """
    # sys.stdout.write
    return f"\x1b[{30 + fore_color.value}m" + f"\x1b[{40 + back_color.value}m" + f"\x1b[{style.value}m" + text + "\x1b[0m"


def remove_bad_characters(save_name:str):
    """
    Removes all characters that can't be in file/folder names.\n
    (\/:*"?:<>|)
    """
    bad_chars = ["\\", "/", ":", "*", "\"", "?", ":", "<", ">", "|"]
    for char in bad_chars:
        save_name = save_name.replace(char, "")
    return save_name