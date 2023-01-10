"""
EditPy is a lightweight, text-based text editor.

© 2022 GoodCoderBBoy
"""

from platform import system

if system() != "Windows":
    raise EnvironmentError("EditPy cannot run on this Operating System.")

from os import get_terminal_size, remove, startfile
from os.path import abspath, basename
from pyperclip import copy, paste
from msvcrt import getch, kbhit
from re import split, sub
from time import sleep

from typing import Literal, Optional, Self, Type, overload
from types import TracebackType

try:
    from highlight import Highlight, escapeansi, indexansi, insertansi # type: ignore

    highlight = Highlight().__call__
except ImportError:
    def highlight(extension: str, text: str) -> str: return text
    def escapeansi(text: str) -> str: return text
    def indexansi(text: str, start: int, stop: Optional[int]=None, step: Optional[int]=1) -> str: return text[start:(stop or len(text)):(step or 1)]
    def insertansi(text: list[str], pos: int, t: str, a: Optional[bool]=False) -> list[str]: text.insert(pos, t); return text


class EditPy:
    def __init__(self, file: Optional[str]=None) -> None:
        self.mode = 0 # 0: edit mode and 1: command mode

        self.restore_help() # restores help file
        self.open(file)

        if file is None:
            self.text = "Press ctrl+/ to open EditPy help.\n" # contents
            self.ci = 34 # caret index

        self.footer = "" # footer
        self.fi = 0 # footer caret index
        self.fs = 0 # footer selection size

    def restore_help(self) -> None:
        try:
            with open("help", "x", encoding="utf-8") as f:
                f.write("Welcome to EditPy.\n\n\nGeneric:\n           esc: enter/exit command mode\n       up/down: scroll up/down\n    left/right: move caret left/right\n     ctrl+left: increase selection to left\n    ctrl+right: increase selection to right\n\nCommand Mode:\n         enter: input command\n             a: select all\n    h[<t>]/<r>: replace regex <r> with forward-slash-less text <t>\n     n[<path>]: create and open new file, with optional path\n     o[<path>]: open <path> or empty file\n             p: print current file\n             q: quit editor\n     s[<path>]: save or save to <path>\n             w: close file\n             ?: opens help\n      =[index]: moves caret to <index>\n\nShortcuts:\n        ctrl+a: select all\n        ctrl+c: copy text\n        ctrl+q: quit editor\n        ctrl+n: create file\n        ctrl+o: open file\n        ctrl+s: save file\n        ctrl+v: paste text\n        ctrl+w: close file\n        ctrl+/: open help\n\nDialogs:\n           esc: cancel action\n         enter: confirm input\n    arrow keys: move caret/select option\n")

        except FileExistsError:
            pass

    def open(self, path: Optional[str]=None) -> None:
        self.file = path # filepath
        self.text = "" # contents

        if self.file is not None:
            self.file = abspath(self.file.rstrip("/"))

            with open(self.file, "r", encoding="utf-8") as f:
                self.text = sub(r"\r\n|\r|\n", "\n", f.read()) # standardise line ending

        self.ci = 0 # caret index
        self.cx = 0 # caret x
        self.cy = 0 # caret y
        self.cs = 0 # selection size

        self.sx = 0 # scroll x
        self.sy = 0 # scroll y

        self.saved = True # file is saved

        self.calculate()

    def save(self, path: Optional[str]=None) -> None:
        if self.file is None:
            o = (path or self.dialog("save"))

            if o is None:
                return

            self.file = abspath(o.rstrip("/"))

        with open(self.file, "w", encoding="utf-8") as f:
            f.write(self.text)

        self.saved = True

    def print(self) -> None:
        tmp = None

        try:
            with open("tmp.txt", "r", encoding="utf-8") as t:
                tmp = t.read()
        except FileNotFoundError:
            pass

        with open("tmp.txt", "w", encoding="utf-8") as t:
            t.write(self.text)

        startfile(abspath("tmp.txt"), "print")

        sleep(0.5)

        if tmp is None:
            remove("tmp.txt")
        else:
            with open("tmp.txt", "w", encoding="utf-8") as t:
                t.write(tmp)

    def getfilename(self) -> str:
        if self.file is None:
            return "new file"
        else:
            return basename(self.file)

    def reset(self) -> None:
        print(end="\x1b[2J\x1b[H\x1b[?25h\x1b[?47l")

    def ellipse(self, text: str, size: int, rtrunc: bool=True) -> str:
        if size < 4:
            return ""

        if len(text) > size:
            return ("... " * (not rtrunc)) + text[(len(text) - size + 4) * (not rtrunc):(size - 4 if rtrunc else len(text))] + (" ..." * rtrunc)

        return text

    @overload
    def calculate(self, t: Literal[True]=...) -> list[str]: pass

    @overload
    def calculate(self, t: Literal[False]=...) -> None: pass

    def calculate(self, t=True):
        self.size = get_terminal_size()

        text = [l + " " for l in split(r"\n", highlight(self.getfilename().rsplit(".", 1)[-1], self.text))]

        self.lines = len(text)
        self.padding = len(str(self.lines))

        line = []

        i = self.ci
        for y, l in enumerate(text):
            if t:
                line = list(indexansi(l, self.sx, self.sx + self.size.columns - self.padding - 1))

            for x in range(len(escapeansi(l)) * (i >= -self.cs - 2)):
                i -= 1

                if i == -1:
                    self.cx = x
                    self.cy = y

                    if t:
                        for j in range(min(len(line), x - self.sx + self.cs + 1), x - self.sx, -1):
                            line = insertansi(line, j, "\x1b[7m", a=True)

                elif x == 0 and -self.cs - 2 < i < 0 and t:
                    for j in range(min(len(line), self.cs + i - self.sx + 2), 0, -1):
                        line = insertansi(line, j, "\x1b[7m", a=True)

                elif i == -self.cs - 2 and t:
                    line = insertansi(line, min(len(line), x - self.sx + 1), "\x1b[27m", a=True)

            if t:
                text[y] = f"\x1b[2m{str(y + 1).rjust(self.padding)}\x1b[22m {''.join(line)}\x1b[0m\n"

        if t:
            return text[self.sy:self.sy + self.size.lines - self.mode - 1]

    def scroll(self) -> None:
        self.calculate(False)

        xthreshhold = min(self.cs, max(0, self.text.find("\n", self.ci) - self.ci)) - (self.size.columns - self.padding - 1)
        ythreshhold = self.size.lines - self.mode - 2

        if self.sx > self.cx - 3:
            self.sx = max(0, self.cx - 3)

        elif self.sx < self.cx + xthreshhold + 3:
            self.sx = self.cx + xthreshhold + 3

        if self.sy > self.cy:
            self.sy = min(self.lines, self.cy)

        elif self.sy < self.cy - ythreshhold:
            self.sy = max(0, self.cy - ythreshhold)

    def redraw(self, flush: bool=True) -> None:
        text = self.calculate()

        header = f"{self.cx},{self.cy} ({self.cs + 1})"
        self.status = f"EditPy - {'(unsaved) ' * (not self.saved)}{self.getfilename()}"

        print(
            "\x1b[2J\x1b[H" + header[:self.size.columns] + (" " * max(2, self.size.columns - len(header + self.status))) + self.ellipse(self.status, self.size.columns - len(header) - 2),
            "".join(text).removesuffix("\n"),
            sep="\n",
            end="\n" * (self.size.lines - self.lines - self.mode - 1),
            flush=False
        )

        if self.mode == 1:
            footer = self.ellipse(self.footer + " ", self.size.columns - self.padding - 1)
            footer = footer[:self.fi] + "\x1b[7m" + footer[self.fi:self.fi + self.fs + 1] + "\x1b[27m" + footer[self.fi + self.fs + 1:]

            print(end=f"\n{' ' * (self.padding - 1)}:{footer}\x1b[0m", flush=flush)

    @overload
    def dialog(self, why: Literal["save"]=...) -> str | None: pass

    @overload
    def dialog(self, why: Literal["open"]=...) -> str | None: pass

    @overload
    def dialog(self, why: Literal["close"]=...) -> bool | None: pass

    def dialog(self, why="save"):
        msgs = {
            "save": "\x1b[2;{x}H┌──────────────────┐\x1b[3;{x}H│  Enter filepath  │\x1b[4;{x}H│ ┌──────────────┐ │\x1b[5;{x}H│ │ {n} │ │\x1b[6;{x}H│ └──────────────┘ │\x1b[7;{x}H└──────────────────┘",
            "open": "\x1b[2;{x}H┌──────────────────┐\x1b[3;{x}H│  Enter filepath  │\x1b[4;{x}H│ ┌──────────────┐ │\x1b[5;{x}H│ │ {n} │ │\x1b[6;{x}H│ └──────────────┘ │\x1b[7;{x}H└──────────────────┘",
            "close": "\x1b[2;{x}H┌──────────────────┐\x1b[3;{x}H│  Close unsaved?  │\x1b[4;{x}H│   {ty}  {tn}   │\x1b[5;{x}H│   {my}  {mn}   │\x1b[6;{x}H│   {by}  {bn}   │\x1b[7;{x}H└──────────────────┘"
        }

        di = 0 # dialog caret index
        ds = 0 # dialog selection size
        dv = ".txt" # dialog value

        code = 0

        while True:
            try:
                self.redraw(False)

                if why in ["save", "open"]:
                    t = self.ellipse(dv, 11, False).ljust(12)

                    print(end=msgs[why].format(
                        x=round((self.size.columns - 20) / 2),
                        n=t[:di] + "\x1b[7m" + t[di:di + ds + 1] + "\x1b[27m" + t[di + ds + 1:]
                    ), flush=True)

                elif why == "close":
                    print(end=msgs["close"].format(
                        x=round((self.size.columns - 20) / 2),
                        ty=("┌───┐" if di else "▗▄▄▄▖"),
                        tn=("▗▄▄▄▖" if di else "┌───┐"),
                        my=("│ Y │" if di else "▐█\x1b[38;5;234m\x1b[48;5;251mY\x1b[0m█▌"),
                        mn=("▐█\x1b[38;5;234m\x1b[48;5;251mN\x1b[0m█▌" if di else "│ N │"),
                        by=("└───┘" if di else "▝▀▀▀▘"),
                        bn=("▝▀▀▀▘" if di else "└───┘")
                    ), flush=True)

                while not kbhit():
                    self.redraw(False)

                    if why in ["save", "open"]:
                        t = self.ellipse(dv, 11, False).ljust(12)
                        f = di - min(0, 11 - len(dv))

                        print(end=msgs[why].format(
                            x=round((self.size.columns - 20) / 2),
                            n=t[:f] + "\x1b[7m" + t[f:f + ds + 1] + "\x1b[27m" + t[f + ds + 1:]
                        ), flush=True)

                    elif why == "close":
                        print(end=msgs["close"].format(
                            x=round((self.size.columns - 20) / 2),
                            ty=("┌───┐" if di else "▗▄▄▄▖"),
                            tn=("▗▄▄▄▖" if di else "┌───┐"),
                            my=("│ Y │" if di else "▐█\x1b[38;5;234m\x1b[48;5;251mY\x1b[0m█▌"),
                            mn=("▐█\x1b[38;5;234m\x1b[48;5;251mN\x1b[0m█▌" if di else "│ N │"),
                            by=("└───┘" if di else "▝▀▀▀▘"),
                            bn=("▝▀▀▀▘" if di else "└───┘")
                        ), flush=True)

                key = ord(getch())

                if key == 0:
                    code = ord(getch())
            except KeyboardInterrupt:
                key = 3

            if key == 27: # escape
                return

            elif key in [10, 13]: # newline / carriage return
                if why == "open" or (why == "save" and dv.rstrip("/")):
                    return dv.rstrip("/")
                elif why == "close":
                    return bool(di - 1)

            elif key == 0:
                if code == 75 and di + ds > 0: # left
                    if di > 0:
                        di -= 1

                    ds = 0

                elif code == 77 and (di < len(dv) or why == "close"): # right
                    di += ds + 1
                    ds = 0

                elif code == 83 and why in ["save", "open"]: # delete
                    if di < len(dv):
                        dv = dv[:di] + dv[di + ds + 1:]

                        ds = 0

                elif why in ["save", "open"]:
                    if code == 115 and di > 0: # ctrl+left
                        di -= 1

                        if di + 1 < len(dv):
                            ds += 1

                    elif code == 116 and di + ds < len(dv) - 1: # ctrl+right
                       ds += 1

            else:
                if key == 1: # ctrl+a
                    if why in ["save", "open"]:
                        di = 0
                        ds = len(dv) - 1

                elif key == 3: # ctrl+c:
                    if ds > 0 and why in ["save", "open"]:
                        copy(dv[di:di + ds + 1])

                elif key == 8: # backspace
                    if di + ds > 0 and why in ["save", "open"]:
                        if di > 0:
                            di -= (ds == 0)

                        dv = dv[:di] + dv[di + ds + 1:]

                        ds = 0

                elif key == 22: # ctrl+v, sometimes?
                    if why in ["save", "open"]:
                        dv = dv[:di] + sub(r"\r\n|\r|\n", "", paste()) + dv[di + ds + 1:]

                        ds = 0

                elif key < 32: # any other weird sequence
                    pass

                elif why in ["save", "open"]:
                    dv = dv[:di] + chr(key) + dv[di + ds + (ds != 0):]

                    di += 1
                    ds = 0

    def parse_command(self) -> str | None:
        cmd = self.footer[0]
        args = self.footer[1:]

        if cmd == "a":
            self.ci = 0
            self.cs = len(self.text) - 1

        elif cmd == "h" and args:
            s = args.rfind("/")

            if s != -1:
                self.text = sub(args[s + 1:], args[:s], self.text)

        elif cmd == "n":
            if not self.saved:
                if self.dialog("close") in [False, None]:
                    return ""

            p = self.dialog("open")

            if p is not None:
                if p.rstrip("/") != "":
                    with open(abspath(p.rstrip("/")), "w", encoding="utf-8"):
                        pass

                self.open(p.rstrip("/") or None)

        elif cmd == "o":
            if not self.saved:
                if self.dialog("close") in [False, None]:
                    return ""

            self.open(args.rstrip("/") or None)

        elif cmd == "p":
            self.print()

        elif cmd == "q":
            if not self.saved:
                if self.dialog("close") in [False, None]:
                    return ""

            return

        elif cmd == "s":
            self.save(args)

        elif cmd == "w":
            if not self.saved:
                if self.dialog("close") in [False, None]:
                    return ""

            self.open()

        elif cmd == "=" and args:
            try:
                if 0 <= int(args) <= len(self.text):
                    self.ci = int(args)
                elif -len(self.text) <= int(args) < 0:
                    self.ci = len(self.text) - int(args) - 1
            except:
                pass

        elif cmd == "?":
            if not self.saved:
                if self.dialog("close") in [False, None]:
                    return ""

            self.open("help")

        return ""

    def __call__(self) -> None:
        print(end="\x1b[?47h\x1b[?25l")

        code = 0

        while True:
            self.redraw()

            try:
                while not kbhit():
                    self.redraw()

                key = ord(getch())

                if key == 0:
                    code = ord(getch())
            except KeyboardInterrupt:
                key = 3

            if self.mode == 0:
                if key == 0:
                    if code == 72: # up
                        if self.sy > 0:
                            self.sy -= 1

                    elif code == 75 and self.ci + self.cs > 0: # left
                        if self.ci > 0:
                            self.ci -= 1

                        self.cs = 0

                    elif code == 77 and self.ci < len(self.text): # right
                        self.ci += self.cs + 1
                        self.cs = 0

                    elif code == 80: # down
                        if self.sy < self.lines - 1:
                            self.sy += 1

                    elif code == 83 and self.ci < len(self.text): # delete
                        self.text = self.text[:self.ci] + self.text[self.ci + self.cs + 1:]

                        self.cs = 0

                    elif code == 115 and self.ci > 0: # ctrl+left
                        self.ci -= 1

                        if self.ci + 1 < len(self.text):
                            self.cs += 1

                    elif code == 116 and self.ci + self.cs < len(self.text) - 1: # ctrl+right
                        self.cs += 1

                    if code not in [72, 80]:
                        self.scroll()

                    if code in [83]:
                        self.saved = False

                else:
                    if key == 1: # ctrl+a
                        self.ci = 0
                        self.cs = len(self.text) - 1

                    elif key == 3: # ctrl+c:
                        if self.cs > 0:
                            copy(self.text[self.ci:self.ci + self.cs + 1])

                    elif key == 8: # backspace
                        if self.ci + self.cs > 0:
                            if self.ci > 0:
                                self.ci -= (self.cs == 0)

                            self.text = self.text[:self.ci] + self.text[self.ci + self.cs + 1:]

                            self.cs = 0

                    elif key == 9: # tab:
                        self.text = self.text[:self.ci] + "    " + self.text[self.ci + self.cs + (self.cs != 0):]

                        self.ci += 4
                        self.cs = 0

                        self.saved = False

                    elif key in [10, 13]: # newline / carriage return
                        self.text = self.text[:self.ci] + "\n" + self.text[self.ci + self.cs + (self.cs != 0):]

                        self.ci += 1
                        self.cs = 0

                        self.saved = False

                    elif key == 14: # ctrl+n:
                        if not self.saved:
                            if self.dialog("close") in [False, None]:
                                continue

                        p = self.dialog("open")

                        if p is not None:
                            if p.rstrip("/") != "":
                                with open(abspath(p.rstrip("/")), "w", encoding="utf-8"):
                                    pass

                            self.open(p.rstrip("/") or None)

                    elif key == 15: # ctrl+o:
                        if not self.saved:
                            if self.dialog("close") in [False, None]:
                                continue

                        f = self.dialog("open")

                        if f is not None:
                            self.open(f.rstrip("/") or None)

                    elif key == 17: # ctrl+q
                        if not self.saved:
                            if self.dialog("close") in [False, None]:
                                continue

                        break

                    elif key == 19: # ctrl+s:
                        self.save()

                    elif key == 22: # ctrl+v, sometimes?
                        self.text = self.text[:self.ci] + sub(r"\r\n|\r|\n", "\n", paste()) + self.text[self.ci + self.cs + 1:]

                        self.cs = 0

                    elif key == 23: # ctrl+w:
                        if not self.saved:
                            if self.dialog("close") in [False, None]:
                                continue

                        self.open()

                    elif key == 27: # escape
                        self.mode = 1

                    elif key == 31: # ctrl+/
                        if not self.saved:
                            if self.dialog("close") in [False, None]:
                                continue

                        self.open("help")

                    elif key < 32: # any other weird sequence
                        pass

                    else: # any other key
                        self.text = self.text[:self.ci] + chr(key) + self.text[self.ci + self.cs + (self.cs != 0):]

                        self.ci += 1
                        self.cs = 0

                        self.saved = False

                    if key != 27:
                        self.scroll()

                    if key in [8, 9, 10, 13, 22]:
                        self.saved = False

                continue

            if key == 0:
                if code == 75 and self.fi + self.fs > 0: # left
                    if self.fi > 0:
                        self.fi -= 1

                    self.fs = 0

                elif code == 77 and self.fi < len(self.footer): # right
                    self.fi += self.fs + 1
                    self.fs = 0

                elif code == 83 and self.fi < len(self.footer): # delete
                    self.footer = self.footer[:self.fi] + self.footer[self.fi + self.fs + 1:]

                    self.fs = 0

                elif code == 115 and self.fi > 0: # ctrl+left
                    self.fi -= 1

                    if self.fi + 1 < len(self.footer):
                        self.fs += 1

                elif code == 116 and self.fi + self.fs < len(self.footer) - 1: # ctrl+right
                    self.fs += 1

            else:
                if key == 1: # ctrl+a
                    self.fi = 0
                    self.fs = len(self.footer) - 1

                elif key == 3: # ctrl+c:
                    if self.fs > 0:
                        copy(self.footer[self.fi:self.fi + self.fs + 1])

                elif key == 8: # backspace
                    if self.fi + self.fs > 0:
                        if self.fi > 0:
                            self.fi -= (self.fs == 0)

                        self.footer = self.footer[:self.fi] + self.footer[self.fi + self.fs + 1:]

                        self.fs = 0

                elif key in [10, 13]: # newline / carriage return
                    if len(self.footer) > 0:
                        output = self.parse_command()

                        if output is None:
                            break

                        else:
                            self.footer = output

                    self.fi = 0
                    self.fs = 0

                elif key == 14: # ctrl+n:
                    if not self.saved:
                        if self.dialog("close") in [False, None]:
                            continue

                    p = self.dialog("open")

                    if p is not None:
                        if p.rstrip("/") != "":
                            with open(abspath(p.rstrip("/")), "w", encoding="utf-8"): # type: ignore
                                pass

                        self.open(p.rstrip("/") or None)

                elif key == 15: # ctrl+o:
                    if not self.saved:
                        if self.dialog("close") in [False, None]:
                            continue

                    f = self.dialog("open")

                    if f is not None:
                        self.open((f or None))

                elif key == 17: # ctrl+q
                    if not self.saved:
                        if self.dialog("close") in [False, None]:
                            continue

                    break

                elif key == 19: # ctrl+s:
                    self.save()

                elif key == 22: # ctrl+v, sometimes?
                    self.text = self.footer[:self.fi] + sub(r"\r\n|\r|\n", "\n", paste()) + self.footer[self.fi + self.fs + 1:]

                    self.cs = 0

                elif key == 23: # ctrl+w:
                    if not self.saved:
                        if self.dialog("close") in [False, None]:
                            continue

                    self.open()

                elif key == 27: # escape:
                    self.mode = 0

                elif key == 31: # ctrl+/
                    if not self.saved:
                        if self.dialog("close") in [False, None]:
                            continue

                    self.open("help")

                elif key < 32: # any other weird sequence
                    pass

                else:
                    self.footer = self.footer[:self.fi] + chr(key) + self.footer[self.fi + self.fs + (self.fs != 0):]

                    self.fi += 1
                    self.fs = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(self, __type: Type[BaseException] | None, __value: BaseException | None, __traceback: TracebackType | None, /) -> None:
        self.reset()


if __name__ == "__main__":
    with EditPy() as e:
        e()
