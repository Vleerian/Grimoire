import markdown
import re
from config import Grimoire_Config

#does what it says on the box
def ParseMarkdownExt(Text):
    Patterns = [
        (r"-(?:>|&gt;)([\w\W]+?)(:?<|&lt;)-", r"<center>\1</center>"),
        (r"(\d+[A-z]+)\d+(?:-1)?", r"\1")
    ]
    Result = Text
    for Pattern in Patterns:
        Result = re.sub(Pattern[0], Pattern[1], Result)
    return Result

#This just applies markdown and Atabang
def Markup(Text):
    Result = Text
    if Grimoire_Config.Enable_Markdown:
        Result = markdown.markdown(Text)
        Result = ParseMarkdownExt(Result)
    return Result
