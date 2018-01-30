import markdown
import re

def ParseAtabang(Text):
    Patterns = [
        [r":![cC]([\w\W]+?)(?:\n|$|<\/)", r"<center>\1</center></"],
        [r":![sS]([\w\W]+?)(?:\n|$|<\/)", r"<spoiler>\1</spoiler></"],
        [r"<p>:![tT]([\w\W]+?)(?:\n|$|<\/p>)", ""]
    ]
    Result = Text
    for Pattern in Patterns:
        Result = re.sub(Pattern[0], Pattern[1], Result)
    return Result

def Markup(Text):
    Result = markdown.markdown(Text)
    Result = ParseAtabang(Result)
    return Result
