from DBHandler import *
from random import choice
from random import shuffle
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
    "Overview": ("Tell me a little about $?.", """
* * *
## Overview
"""),
    "Appearance": ("What does $? look like?", """
* * *
## Appearance
"""),
    "Personality": ("Tell me about how $? acts.", """
* * *
## Personality
"""),
    "Powers": ("What sort of powers or abilities does $? have?", """
* * *
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
    #Common fields for locations
    Location_Fields = {
    "Overview": ("Tell me, what kind of place is $??", """
* * *
## Overview
"""),
    "People": ("Tell me of the people around $?.", """
* * *
## People
"""),
    "Culture": ("Tell me of $?'s culture.'", """
* * *
## Culture
"""),
    "Location": ("Where is $?, how can I find it?.'", """
* * *
## Location
"""),
    "Atmosphere": ("What is it like to spend time in $??.'", """
* * *
## Atmosphere
""")
    }
    #Common fields for items
    Item_Fields = {
    "Overview": ("Tell me, what sort of device is $??", """
* * *
## Overview
"""),
    "Appearance": ("What does this '$?' look like.", """
* * *
## Appearance
"""),
    "Function": ("This $?, what purpose does it serve?.'", """
* * *
## Function
""")
    }
    #Suggestions that show up if no prompts can be had.
    Suggestions = [
    "I wonder what beliefs $? holds.",
    "Do you think $? has any hobbies they're keeping secret?",
    "$?, an interesting name. Where do you think it comes from?",
    "What do you think $? does in their spare time, Zodivikh?",
    "Do you think I'd make friends with $?, Zodivikh?",
    "Tell me, do you think $? is 'evil,' or 'good?'"
    ]
    #The above categories are used for presenting prompts to the user
    #In order to flesh out a page


    #CreatePrompt does what it says. It creates prompts for the user
    def CreatePrompt(self, Book):
        #GenPrompt is used for creating Item/Location/Character Prompts
        #It uses the categories defined and whatever page it's given
        #To see if a prompt needs to be sent.
        def GenPrompt(Item, Collection):
            for SubCategory in Collection.keys():
                if not SubCategory in Item[2].replace("\r", ""):
                    return (
                    Collection[SubCategory][0].replace("$?", Item[0]),
                    Collection[SubCategory][1]
                    )
            return None

        #We need fields & tags so that we can give prompts relevant to a page
        Data = FieldsTagsReadout(Book)
        Ignore = []
        Title = None
        Prompt = None

        #We're gonna go through all the tagged &|| fielded pages to give prompts to fill them out more
        for Point in Data:
            Tag = Point[-1].strip()
            if "Character" in Tag:
                tmp = [self.Common_Fields, self.Common_Features]
                shuffle(tmp)
                for Category in tmp:
                    Prompt = GenPrompt(Point, Category)
                    Title = Point[0]
            elif "Item" in Tag:
                Prompt = GenPrompt(Point, self.Item_Fields)
                Title = Point[0]
            elif "Location" in Tag:
                Prompt = GenPrompt(Point, self.Location_Fields)
                Title = Point[0]
            Ignore.append((Point[0],))

        #Failing that, let's start tagging pages
        if Prompt is None:
            #First thing's first. If the prompt isn't set, that means
            #whatever title was seat above is irrelevant.
            Title = None
            BookData = GetBook(Book, False)
            while len(BookData) > 0:
                #So we need book data. But if we just go through books, it will want to
                #tag pages that are already tagged... this is where the ignore variable
                #we'd been working on comes in handy. We 'ignore' fleshed out pages
                Tmp = BookData.pop()
                if not Tmp in Ignore:
                    Title = Tmp[0]
                    Prompt = ("I know little about " + Title + ", care to tell me what they are?",
                    ":!t Character|Location|Item")
                    BookData = []
            if Title is None:
                #Finally, if there are no pages to tag or flesh out, we'll look for links.
                #If you're in a potential book, or a book with potential pages, it'll give
                #prompts for them.
                Link = RandoLink(Book)
                if not Link is None:
                    Prompt = ("I remember you mentioning " + Link[0] + ", what might that be?",
                    ":!t Character|Location|Item")
                    Title = Link[0]
                else:
                    #And if your book is empty/completely filled out, we'll give a little
                    #seed to encourage more writing
                    if len(Ignore) > 0:
                        Ret = "<sink>"
                        Ret += choice(self.Suggestions).replace("$?", choice(Ignore)[0])
                        Ret += "</sink>"
                        return Ret
                    else:
                        return "<sink>What a sad book this is, Zodivikh.</sink>"

        #And if your book isn't empty, we're gonna fill out a promptarea template to return.
        Finished = loadTemplate("PromptArea")
        Finished = Finished.replace("$PROMPT", Prompt[0])
        Finished = Finished.replace("$APPEND", Prompt[1])
        Finished = Finished.replace("$TITLE", Title)
        Finished = Finished.replace("$BOOK", Book)
        return Finished
