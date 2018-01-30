from DBHandler import *
from random import choice
from main import loadTemplate

class Prompts():
    #Page_Types is used to determine (through a user-set tag) what a page is about
    Page_Types = [
    "Character",
    "Location",
    "Item"
    ]
    #Common fields include general sections you'd expect on a page
    Common_Fields = {
    "Overview": ("Tell me a little about $?.", """* * *
## Overview
"""),
    "Appearance": ("What does $? look like?", """* * *
## Appearance
"""),
    "Personality": ("Tell me about how $? acts.", """* * *
## Personality
"""),
    "Powers": ("What sort of powers or abilities does $? have?", """* * *
## Powers
""")
    }
    #Common features are things you'd expect on a page
    Common_Features = {
    "Age": ("How old is $??", "**Age**: ? |"),
    "Occupation": ("What does $? do for a living?", "**Occupation*: ? |"),
    "Sex": ("What sex is $??", "**Sex**: ? |"),
    "Height": ("How tall is $??", "**Height**: ? |"),
    "Weight": ("How much does $? weigh?", "**Weight**: ? |")
    }
    #The above categories are used for presenting prompts to the user
    #In order to flesh out a page

    def CharacterPrompt(self, Book):
        BookData = GetBook(Book)
        Ignore = [None]
        Data = FieldsTagsReadout(Book)
        Prompt = None
        for Point in Data:
            if Point[-1] == "Character":
                Choice = choice(["Field", "Feature"])
                if Choice == "Field":
                    for Field in self.Common_Fields.keys():
                        if not Field in Point[2]:
                            Prompt = (self.Common_Fields[Field][0].replace("$?", Point[0]),
                            self.Common_Fields[Field][1])
                    for Feature in self.Common_Features.keys():
                        if not Feature in Point[2]:
                            Prompt = (self.Common_Features[Feature][0].replace("$?", Point[0]),
                            self.Common_Features[Feature][1])
                else:
                    for Feature in self.Common_Features.keys():
                        if not Feature in Point[2]:
                            Prompt = (self.Common_Features[Feature][0].replace("$?", Point[0]),
                            self.Common_Features[Feature][1])
                    for Field in self.Common_Fields.keys():
                        if not Field in Point[2]:
                            Prompt = (self.Common_Fields[Field][0].replace("$?", Point[0]),
                            self.Common_Fields[Field][1])
            Ignore.append(Point[0])
        if len(Ignore)-1 == len(BookData):
            Link = RandoLink(Book)
            if Link == None:
                return "<sink>I wonder what pages you'll add next, Zodivikh.</sink>"
            Prompt = ("I remember you mentioning " + Link[0] + ", what might that be?",
            ":!t Character|Location|Item")
            Point = Link
        else:
            Choice = None
            while Choice in Ignore:
                Choice = choice(BookData)[1]
            Prompt = ("I know little about " + Choice + ", care to tell me what they are?",
            ":!t Character|Location|Item")
            Point = (Choice, Book)
        Finished = loadTemplate("PromptArea")
        Finished = Finished.replace("$PROMPT", Prompt[0])
        Finished = Finished.replace("$APPEND", Prompt[1])
        Finished = Finished.replace("$TITLE", Point[0])
        Finished = Finished.replace("$BOOK", Point[1])
        return Finished
