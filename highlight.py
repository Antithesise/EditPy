"""
This is EditPy's Syntax Highlighting Engine.

© 2022 GoodCoderBBoy
"""

from re import match, search, sub

from typing import Optional


Colours = {
    "asterisk": "\x1b[38;2;%d;%d;%dm" % (86, 156, 214),
    "attribute": "\x1b[38;2;%d;%d;%dm" % (156, 220, 254),
    "block": "\x1b[38;2;%d;%d;%dm" % (106, 153, 85),
    "bold": "\x1b[1;38;2;%d;%d;%dm" % (86, 156, 214),
    "class": "\x1b[38;2;%d;%d;%dm" % (78, 201, 176),
    "css": "\x1b[0m",
    "comment": "\x1b[38;2;%d;%d;%dm" % (106, 153, 85),
    "constant": "\x1b[38;2;%d;%d;%dm" % (52, 181, 255),
    "decorator": "\x1b[38;2;%d;%d;%dm" % (220, 220, 170),
    "escape": "\x1b[38;2;%d;%d;%dm" % (215, 186, 125),
    "function": "\x1b[38;2;%d;%d;%dm" % (220, 220, 170),
    "heading": "\x1b[1;38;2;%d;%d;%dm" % (86, 156, 214),
    "identifier": "\x1b[38;2;%d;%d;%dm" % (140, 220, 254),
    "identifier": "\x1b[38;2;%d;%d;%dm" % (140, 220, 254),
    "italic": "\x1b[3m",
    "js": "\x1b[0m",
    "keyword": "\x1b[38;2;%d;%d;%dm" % (79, 151, 214),
    "keyword1": "\x1b[38;2;%d;%d;%dm" % (79, 151, 214),
    "keyword2": "\x1b[38;2;%d;%d;%dm" % (187, 134, 192),
    "list": "\x1b[38;2;%d;%d;%dm" % (86, 156, 214),
    "number": "\x1b[38;2;%d;%d;%dm" % (181, 206, 168),
    "plain": "\x1b[0m",
    "regex": "\x1b[38;2;%d;%d;%dm" % (209, 105, 105),
    "regex2": "\x1b[38;2;%d;%d;%dm" % (206, 145, 120),
    "selector": "\x1b[38;2;%d;%d;%dm" % (215, 186, 125),
    "strikethrough": "\x1b[9m",
    "string": "\x1b[38;2;%d;%d;%dm" % (206, 145, 120),
    "subtag": "\x1b[38;2;%d;%d;%dm" % (140, 220, 254),
    "tag": "\x1b[38;2;%d;%d;%dm" % (128, 128, 128),
    "tagname": "\x1b[38;2;%d;%d;%dm" % (86, 156, 214),
    "value1": "\x1b[38;2;%d;%d;%dm" % (206, 145, 120),
    "value2": "\x1b[38;2;%d;%d;%dm" % (220, 220, 170)
}

class Patterns:
    CSS = [
        (r"/\*(?:[^\*]|\*(?!/))*\*/", "comment"),
        (r"\*", "asterisk"),
        (r"(?s)(?:(?!\W)[^\[\'\"]|#|::|:|@)?(?:\w|\-)+(?:\((?=.*\)))?(?![^\[]*=|[^\'\"\[]*[\'\"])(?=[^;]*\{)", "selector"),
        (r"(?:\w|\-)+(?=[\s]*[:=])", "attribute"),
        (r"\"[^\n\"]*\"|\'[^\n\']*\'", "string"),
        (r"[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:cm|mm|in|px|pt|pc|em|ex|ch|rem|vw|vh|vmin|vmax|\%)?", "number"),
        (r"[^:(), ]+(?= *\([^:]*;)", "value2"),
        (r"[^:(), ]+(?=[^:]*;)", "value1"),
        (r".", "plain")
    ]
    HTML = [
        (r"<--.*-->", "comment"),
        (r"</|<!|<\?|<|/>|\?>|>", "tag"),
        (r"(?a)[^ \"\n=<>]+(?=.*[/]?>)(?!=|<|[^> ]|[^>]*<)|\&(?:#x|#)?[a-zA-z0-9]{2,};", "tagname"),
        (r"(?s)(?:.(?!<script))*(?=</script>)", "js"),
        (r"(?s)(?:.(?!<style))*(?=</style>)", "css"),
        (r"\"[^\n\"]*\"|\'[^\n\']*\'", "string"),
        (r"(?a)[^ \"\n=<>]+(?==)", "subtag"),
        (r".", "plain")
    ]
    JSON = [
        (r"\btrue\b|\bfalse\b|\bnull\b", "keyword"),
        (r"[-]?[0-9]+(?:\.[0-9]+)?", "number"),
        (r"\"[^\n\"]*\"(?= *:)", "identifier"),
        (r"\"[^\n\"]*\"", "string"),
        (r".", "plain")
    ]
    MARKDOWN = [
        (r"^(?:\*\*\*|\-\-\-|\_\_\_) *$", "plain"),
        (r"\\[`!#*()-_+{}\[\]\\.]", "escape"),
        (r"(?P<del>\*\*|__)([^\*_].*)?(?!\\)(?P=del)", "bold"),
        (r"(?<!_)(?P<del>[\*_])([^\*_].*)?(?!\\)(?P=del)", "italic"),
        (r"(?P<tilde>\~{2,}).*(?!\\)(?P=tilde)", "strikethrough"),
        (r"^(?: *>)+", "block"),
        (r"\#{1,6}(?: +[^\#\n]*)?", "heading"),
        (r"^ *[0-9]+\.|^ *[\-\*\+] ", "list"),
        (r"(?P<multitick>\`{3,})[^\`]*(?!\\)(?P=multitick)|(?P<tick>\`{1,2})[^\`\n]*(?!\\)(?P=tick)|[^\[\n\]]+(?!\\)(?=\])", "string"),
        (r".", "plain")
    ]
    PYTHON = [
        (r"\#[^\n]*", "comment"),
        (r"(?s)(?:r[bf]?|[bf]?r)\"\"\"(?:[^\\]|\\.)*\"\"\"|(?:r[bf]?|[bf]?r)\'\'\'(?:[^\\]|\\.)*\'\'\'|(?:r[bf]?|[bf]?r)\"(?:[^\"\\\n]|\\.)*\"|(?:r[bf]?|[bf]?r)\'(?:[^\'\\\n]|\\.)*\'", "regex"),
        (r"\bdef\b|\bpass\b|\blambda\b|\bglobal\b|\bnonlocal\b|\bTrue\b|\bFalse\b|\bNone\b|\bb(?=[\"\'])|\bf(?=[\"\'])|\bu(?=[\"\'])|\\ *\n", "keyword1"),
        (r"\bwhile\b|\bfor\b|\bif\b|\belif\b|\belse\b|\bcontinue\b|\bbreak\b|\btry\b|\bexcept\b|\bfinally\b|\bassert\b|\braise\b|\bfrom\b|\bwith\b|\bas\b|\bawait\b|\basync\b|\breturn\b|\byield\b|\bdel\b|\band\b|\bor\b|\bnot\b|\bin\b|\bis\b", "keyword2"),
        (r"(?a)(?:import|class) +(?:[a-zA-Z_]\w*(?: *\. *)?)+|(?:[a-zA-Z_]\w*(?: *\. *)?)+ +import|\bbool\b|\bint\b|\bfloat\b|\bcomplex\b|\blist\b|\btuple\b|\brange\b|\bstr\b|\bbytes\b|\bbytearray\b|\bmemoryview\b|\bset\b|\bfrozenset\b|\bdict\b|\bobject\b|\bfunction\b|\btype\b|\bArithmeticError\b|\bAssertionError\b|\bAttributeError\b|\bBaseException\b|\bBlockingIOError\b|\bBrokenPipeError\b|\bBufferError\b|\bBytesWarning\b|\bConnectionAbortedError\b|\bChildProcessError\b|\bConnectionError\b|\bConnectionRefusedError\b|\bConnectionResetError\b|\bDeprecationWarning\b|\bEncodingWarning\b|\bEOFError\b|\bException\b|\bFileExistsError\b|\bFileNotFoundError\b|\bFloatingPointError\b|\bFutureWarning\b|\bGeneratorExit\b|\bImportError\b|\bImportWarning\b|\bIndentationError\b|\bIndexError\b|\bInterruptedError\b|\bIsADirectoryError\b|\bKeyboardInterrupt\b|\bKeyError\b|\bLookupError\b|\bMemoryError\b|\bModuleNotFoundError\b|\bNameError\b|\bNotADirectoryError\b|\bNotImplementedError\b|\bOverflowError\b|\bPendingDeprecationWarning\b|\bPermissionError\b|\bProcessLookupError\b|\bRecursionError\b|\bReferenceError\b|\bResourceWarning\b|\bRuntimeError\b|\bRuntimeWarning\b|\bStopAsyncIteration\b|\bStopIteration\b|\bSyntaxError\b|\bSyntaxWarning\b|\bSystemError\b|\bSystemExit\b|\bTabError\b|\bTimeoutError\b|\bTypeError\b|\bUnboundLocalError\b|\bUnicodeDecodeError\b|\bUnicodeEncodeError\b|\bUnicodeError\b|\bUnicodeTranslateError\b|\bUnicodeWarning\b|\bUserWarning\b|\bValueError\b|\bWarning\b|\bZeroDivisionError\b", "class"),
        (r"(?a)\@[a-zA-Z_]\w*(?:\(.*\))?(?=\n(\s)*def )", "decorator"),
        (r"(?as)\b[a-zA-Z_]\w*(?= *\()", "function"),
        (r"(?a)\b[A-Z_][A-Z0-9_]*\b", "constant"),
        (r"(?a)\b[a-zA-Z_]\w*\b", "identifier"),
        (r"(?i)\b[-+]?(?:0e|(?P<bin>0b)|(?P<oct>0o)|(?P<hex>0x))?(?(bin)[01]+|(?(oct)[0-7]+|(?(hex)[0-9a-f]+|[0-9]+)))\.?(?(bin)[01]*|(?(oct)[0-7]*|(?(hex)[0-9a-f]*|[0-9]*)))\b", "number"),
        (r"\"\"\"(?:(?!\"\"\")[^\\]|\\[0-9bfnortux\\\"\'\n])*\"\"\"|\'\'\'(?:(?!\'\'\')[^\\]|\\[0-9bfnortux\\\"\'\n])*\'\'\'|\"(?:[^\"\\\n]|\\[0-9bfnortux\\\"\'\n])*\"|\'(?:[^\'\\\n]|\\[0-9bfnortux\\\"\'\n])*\'", "string"),
        (r".", "plain")
    ]
    URL = (
        r"\b(?<![@.,%&#-])(?P<protocol>\w{2,10}\:\/\/)(?:(?:\w|\&\#\d{1,5};)[.-]?)+(?:\.(?:[a-z]{2,15})|(?(protocol)(?:\:\d{1,6})|(?!)))\b(?![@])(?:\/)?(?:(?:[\w\d\?\-=#:%@&.;])+(?:\/(?:(?:[\w\d\?\-=#:%@&;.])+))*)?(?<![.,?!-])",
        lambda m: f"\x1b[4m{m.group(0)}\x1b[24m"
    )

class Highlight:
    def __call__(self, extension: str, text: str) -> str:
        return self.__getattribute__(extension.lower() if extension.lower() in "css html json md py svg txt xml".split() else "txt")(text)

    def css(self, text: str) -> str:
        text = sub(r"(?m)^\n(?=\n*(?P<level>(?:    )+))", lambda m: m.group("level") + "\n", text.replace("\t", "    ")) + "\n"
        tokens = []

        while len(text):
            for p, v in Patterns.CSS:
                m = match(p, text)

                if m is not None:
                    tokens.append((v, m.group(0)))
                    text = text[m.end(0):]

                    break
            else:
                tokens.append((None, "\n"))
                text = text[1:]

        for t, v in tokens:
            if t:
                if v == " ":
                    text += v
                elif t == "selector":
                    text += Colours["selector"] + v.replace("\n", "\n" + Colours["selector"]).replace("(", "\x1b[0m(" + Colours["selector"]) + "\x1b[0m"
                elif t == "string":
                    text += Colours["string"] + sub(r"\\(?![<>])\S", lambda m: Colours["escape"] + m.group(0) + Colours["string"], v).replace("\n", "\n" + Colours["string"]) + "\x1b[0m"
                else:
                    text += Colours[t] + v.replace("\n", "\n" + Colours[t]) + "\x1b[0m"
            else:
                text += "\n"

        while search(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", text):
            text = sub(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", "\x1b[0m" + r"\1", text)

        text = sub(*Patterns.URL, text)

        return text.removesuffix("\n")

    def html(self, text: str, lang: str="HTML") -> str:
        text = sub(r"(?m)^\n(?=\n*(?P<level>(?:    )+))", lambda m: m.group("level") + "\n", text.replace("\t", "    ")) + "\n"
        tokens = []

        while len(text):
            for p, v in Patterns.HTML:
                m = match(p, text)

                if m is not None:
                    tokens.append((v, m.group(0)))
                    text = text[m.end(0):]

                    break
            else:
                tokens.append((None, "\n"))
                text = text[1:]

        for t, v in tokens:
            if t:
                if v == " ":
                    text += v
                elif t == "css":
                    text += self.css(v)
                else:
                    text += Colours[t] + v.replace("\n", "\n" + Colours[t]) + "\x1b[0m"
            else:
                text += "\n"

        while search(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", text):
            text = sub(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", "\x1b[0m" + r"\1", text)

        text = sub(*Patterns.URL, text)

        return text.removesuffix("\n")

    def json(self, text: str) -> str:
        text = sub(r"(?m)^\n(?=\n*(?P<level>(?:    )+))", lambda m: m.group("level") + "\n", text.replace("\t", "    ")) + "\n"
        tokens = []

        while len(text):
            for p, v in Patterns.JSON:
                m = match(p, text)

                if m is not None:
                    tokens.append((v, m.group(0)))
                    text = text[m.end(0):]

                    break
            else:
                tokens.append((None, "\n"))
                text = text[1:]

        for t, v in tokens:
            if t:
                if v == " ":
                    text += v
                else:
                    text += Colours[t] + v.replace("\n", "\n" + Colours[t]) + "\x1b[0m"
            else:
                text += "\n"

        while search(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", text):
            text = sub(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", "\x1b[0m" + r"\1", text)

        text = sub(*Patterns.URL, text)

        return text.removesuffix("\n")

    def md(self, text: str) -> str:
        text = sub(r"(?m)^\n(?=\n*(?P<level>(?:    )+))", lambda m: m.group("level") + "\n", text.replace("\t", "    ")) + "\n"
        tokens = []

        while len(text):
            for p, v in Patterns.MARKDOWN:
                m = match(p, text)

                if m is not None:
                    tokens.append((v, m.group(0)))
                    text = text[m.end(0):]

                    break
            else:
                tokens.append((None, "\n"))
                text = text[1:]

        for t, v in tokens:
            if t:
                if v == " ":
                    text += v
                else:
                    text += Colours[t] + v.replace("\n", "\n" + Colours[t]) + "\x1b[0m"
            else:
                text += "\n"

        while search(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", text):
            text = sub(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", "\x1b[0m" + r"\1", text)

        text = sub(*Patterns.URL, text)

        return text.removesuffix("\n")

    def py(self, text: str, fstrings: bool=True) -> str:
        text = sub(r"(?m)^\n(?=\n*(?P<level>(?:    )+))", lambda m: m.group("level") + "\n", text.replace("\t", "    ")) + "\n"
        tokens = []

        while len(text):
            for p, v in Patterns.PYTHON:
                m = match(p, text)

                if m is not None:
                    tokens.append((v, m.group(0)))
                    text = text[m.end(0):]

                    break
            else:
                tokens.append((None, "\n"))
                text = text[1:]

        for t, v in tokens:
            if t:
                el = Colours[t] + f"{v}\x1b[0m"

                if v == " ":
                    el = " "
                elif t == "string":
                    if text.endswith(Colours["keyword1"] + "f\x1b[0m") and fstrings:
                        el = sub((r"\{[^\"\\\}]+\}" if v[0] == "\"" else r"\{[^\'\\\}]+\}"), lambda m: self.py(m.group(0), fstrings=False), v)
                        el = sub(r"\\(?= *\n)", lambda m: Colours["keyword1"] + "\\" + Colours["string"], el)
                    else:
                        el = sub(r"\%[diouxXeEfFgGcrs\%]|\{[a-zA-Z_]\w*\}|\\(?= *\n)", lambda m: Colours["keyword1"] + m.group(0) + Colours["string"], v)

                    el = Colours["string"] + sub(r"\\[ux][0-9a-f]+|\\[0-9]+|\\(?![<>])\S", lambda m: Colours["escape"] + m.group(0) + Colours["string"], el) + "\x1b[0m"
                elif t == "class" and el.endswith(" import\x1b[0m"):
                    el = Colours["class"] + el.removesuffix("import\x1b[0m").replace(".", "\x1b[0m." + Colours["class"]) + Colours["keyword2"] + "import\x1b[0m"
                elif t == "class" and el.startswith("import"):
                    el = Colours["keyword2"] + "import " + Colours["class"] + el.split(" ", 1)[-1].replace(".", "\x1b[0m." + Colours["class"])
                elif t == "class" and el.startswith(Colours["class"] + "class"):
                    el = Colours["keyword1"] + "class " + Colours["class"] + el.split(" ", 1)[-1]
                elif t in ["decorator", "regex"]:
                    el = v

                    if t == "regex":
                        el = sub(r"\[(?:\^)?|\]", lambda m: Colours["regex2"] + m.group(0) + Colours["regex"], el)
                        el = sub(r"\\[\\~!@#$%\^&*()_+`1234567890-={}|\[\]:\";'?,./CEFGHIJKLMNOPQRTUVXYacefghijklmnopqrtuvxyz]|[*+]", lambda m: Colours["escape"] + m.group(0) + Colours["regex"], el).replace("|", "\x1b[0m|" + Colours["regex"])
                        el = sub(r"\(\?(?:\(\w+\)|\<\=|\<\!|\=|\!)", lambda m: f"\x1b[0m{m.group(0)}" + Colours["regex"], el)
                        el = sub(r"\?P\=\w+|\?P\<\w+\>|\(\?[aiLmsux]{1,7}(?:\-[imsx]{1,4})?\)", lambda m: Colours["keyword1"] + m.group(0) + Colours["regex"], el)

                    el = Colours["keyword1"] + (el[:2] if el[1] in 'bfr' else el[0]) + Colours[t] + el.lstrip('bfr@') + "\x1b[0m"
                elif t == "plain":
                    el = f"\x1b[0m{v}"

                el = el.replace("\n", "\n" + Colours[t])
            else:
                el = "\n"

            text += el

        while search(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", text):
            text = sub(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", "\x1b[0m" + r"\1", text)

        text = sub(*Patterns.URL, text)

        return text.removesuffix("\n")

    def svg(self, text: str) -> str:
        return self.html(text)

    def txt(self, text: str) -> str:
        text = sub(r"(?m)^\n(?=\n*(?P<level>(?:    )+))", lambda m: m.group("level") + "\n", text.replace("\t", "    ")) + "\n"

        while search(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", text):
            text = sub(r"\x1b\[0m([^\x1b]*)(?:\x1b\[0m)+", "\x1b[0m" + r"\1", text)

        text = sub(*Patterns.URL, text)

        return text.removesuffix("\n")

    def xml(self, text: str) -> str:
        return self.html(text)

def escapeansi(text: str) -> str:
    return sub(r"[\x1b\x9b][\[\]]?[\=\?]?(?:[0-9]+(?:\;[0-9]+)*)?[a-zA-Z]", "", text)

def indexansi(text: str, start: int, stop: Optional[int]=None, step: Optional[int]=1) -> str:
    res = ""
    i = 0
    x = 0

    lim = (stop or len(text))

    if lim < 0:
        lim = min(len(text) + lim, len(text))
    else:
        lim = min(lim, len(text))

    while x < len(text):
        c = text[x]

        e = match(r"[\x1b\x9b][\[\]]?[\=\?]?(?:[0-9]+(?:\;[0-9]+)*)?[a-zA-Z]", text[x:])

        if e:
            x += len(e.group(0))
            res += e.group(0)

            continue
        else:
            x += 1


        if (i + start) % (step or 1) == 0 and start <= i and i < lim:
            res += c

        i += 1

    return res

def insertansi(text: list[str], pos: int, t: str, a: Optional[bool]=False) -> list[str]:
    res = []
    i = 0
    x = 0

    while x < len(text):
        c = text[x]

        e = match(r"[\x1b\x9b][\[\]]?[\=\?]?(?:[0-9]+(?:\;[0-9]+)*)?[a-zA-Z]", "".join(text[x:]))

        if e:
            x += len(e.group(0))
            res += list(e.group(0))

            continue

        x += 1

        if i == pos - int(bool(a)):
            res += list(t)

        res += [c]

        i += 1

    return res