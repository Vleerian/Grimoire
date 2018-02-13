import sqlite3
import urllib
import re
from config import Grimoire_Config

#Setup the database connection
DB = sqlite3.connect(Grimoire_Config.Database_Name+".db")
Cursor = DB.cursor()

#This function pulls all data related to a page
def GetPage(Book, Page):
	#First, we nee to make sure that any unicode characters are restored, then grab the page data
	Page = urllib.parse.unquote(Page)
	Cursor.execute("SELECT * FROM Pages WHERE BookName = ? AND PageName = ?", (Book, Page))
	PageData = Cursor.fetchone()
	if not PageData == None:
		#Now that we have the page's ID, we can grab it's content
		Cursor.execute("SELECT Body FROM Content WHERE PageID = ? AND Valid = 1 LIMIT 1", (PageData[0], ))
		PageContent = Cursor.fetchone()
		#Now we append the content to the basic page data
		PageData += PageContent
		#Last thing we need are the tags.
		Cursor.execute("SELECT group_concat(Tag, \", \") FROM Tags WHERE PageID = ?", (PageData[0], ))
		Tags = Cursor.fetchone()
		PageData += Tags
		return PageData
	else:
		#no page was found
		return None


#This fetches a page's overview
def GetOverview(PageID):
	Cursor.execute("SELECT FieldContent FROM Fields WHERE PageID = ? AND FieldName LIKE '%Overview%' LIMIT 1", (PageID, ))
	Overview = Cursor.fetchone()
	return Overview[0]


#This fetches a page's type
def GetType(PageID):
	Cursor.execute("SELECT GROUP_CONCAT(Tag, \",\") FROM Tags WHERE PageID = ? AND Tag IN(\"Character\", \"Tag\", \"Location\", \"Race\") LIMIT 1", (PageID, ))
	Overview = Cursor.fetchone()
	return Overview[0]


#This function gets the Book/Page pairing based on an ID
def FromID(id : int):
	Cursor.execute("SELECT PageName, BookName FROM Pages WHERE PageID = ?", (id, ))
	Data = Cursor.fetchone()
	return Data[1] + "/" + Data[0]


#This function gets all the pages from a book
def GetBook(Book, IDs = True):
	if IDs:
		Cursor.execute("SELECT PageID, PageName FROM Pages WHERE BookName = ?", (Book, ))
	else:
		Cursor.execute("SELECT PageName FROM Pages WHERE BookName = ?", (Book, ))
	return Cursor.fetchall()


#This function gets all books
def GetBooks():
	Cursor.execute("SELECT BookName FROM Pages GROUP BY BookName")
	return Cursor.fetchall()


#This fetches all potential books
def GetPotentialBooks():
	Cursor.execute("SELECT Book FROM Linked WHERE Book NOT IN (SELECT BookName FROM Pages) GROUP BY BOOK")
	return Cursor.fetchall()


#This fetches all the the pages in a 'potential book'
def GetPotentialBook(Book):
	Cursor.execute("SELECT Book, Name FROM Linked WHERE Book = ?", (Book, ))
	return Cursor.fetchall()


#This function adds a new page
def NewPage(Book, Page, Content, Tags):
	try:
		Cursor.execute("INSERT INTO Pages (PageName, BookName) VALUES (?, ?)", (Page,Book,))
		PageID = Cursor.lastrowid
		Cursor.execute("INSERT INTO Content(PageID, Valid, Body) VALUES(?,?,?)",(PageID, 1, Content,))
		for tag in Tags.split(", "):
			Cursor.execute("INSERT INTO Tags(PageID, Tag) VALUES(?,?)",(PageID, tag,))
		DB.commit()
		ContentParser(PageID, Content)
		return True
	except Exception as E:
		Grimoire_Config.HandleErrMsg(E)
		return False


#this function updates an existing page
def UpdatePage(Data, Content, Tags):
	try:
		Cursor.execute("INSERT INTO Content(PageID, Valid, Body) VALUES(?,?,?)", (Data[0], 1, Content,))
		if Tags is not None:
			Cursor.execute("DELETE FROM Tags WHERE PageID = ?", (Data[0],))
			Tags = Tags.split(", ")
			for tag in Tags:
				Cursor.execute("INSERT INTO Tags(PageID, Tag) VALUES(?,?)",(Data[0], tag.strip(),))
		DB.commit()
		ContentParser(Data[0], Content)
		return True
	except Exception as E:
		Grimoire_Config.HandleErrMsg(E)
		return False


#this function searches for duplicate rows. Any old rows that aren't on the new page are deleted
def HandleDupes(PageID, NewCol, OldCol, Table, Column):
	for Item in OldCol:
		#we use .strip() here to remove any inconvenient trailing whitespace
		if Item[0].strip() in NewCol:
			pass
		else:
			Cursor.execute("DELETE FROM "+Table+" WHERE PageID = ? AND "+Column+" = ?", (PageID, Item[0].strip()))


#Handles 'Date' fields, and links to the owner page
def HandleDate(PageID, Date):
	#We break down a date (1996AD1-1) into usable bits
	Matches = re.findall(r"(\d+)([A-z]+)(\d+)(-1)?", Date)[0]
	#1996AD1(-1)? indicates if we want the year order to be reversed
	Reversed = 0
	if Matches[3] is not None and Matches[3] is not '':
		Reversed = 1
	SQL = "INSERT INTO Dates(PageID, Year, EraName, EraOrder, Reversed) VALUES(?,?,?,?,?)"
	try:
		Cursor.execute(SQL, (PageID, Matches[0], Matches[1], Matches[2], Reversed))
		DB.commit()
	except sqlite3.IntegrityError as E:
		return
	except Exception as E:
		Grimoire_Config.HandleErrMsg(E)

#this function handles all inserts into Fields and Tags.
def HandleInserts(Matches, PageID, SQL):
	#NewCollection is used for HandleDupes
	NewCollection = []
	for Item in Matches:
		NewCollection.append(Item[0])
		try:
			#We use the SQL, and unpack the Item tuple to get a complete SQL statement
			if isinstance(Item, str):
				Cursor.execute(SQL, (PageID, Item,))
			else:
				Cursor.execute(SQL, (PageID, *Item,))
			DB.commit()
		except sqlite3.IntegrityError:
			#There is already a trigger in the database for handling duplicate entries
			#So we don't need to take any action here
			pass
		except Exception as E:
			Grimoire_Config.HandleErrMsg(E)
	return NewCollection


#This function searches content for links to other pages. If the page doesn't exist, we'll
#add it to the 'potential pages' table for future prompts
def SearchForLinks(Text):
	Matches = re.findall(r'\[[\w\W]+?\]\(([\w\W]+?)\)', Text)
	for Match in Matches:
		if re.match("[\w\W]+?\/[\w\W]+", Match[1:]):
			try:
				Cursor.execute("INSERT INTO Linked(Book, Name) VALUES(?,?)", Match[1:].split("/")[1:])
			except sqlite3.IntegrityError:
				pass
			except Exception as E:
				Grimoire_Config.HandleErrMsg(E)


#This function parses a page's content to find all header elements and tags
#It makes use of the HandleDupes and HandleInserts functions
def ContentParser(PageID, Content):
	#The function is defined in here so that we can make use of PageID and Content, without having to pass it around
	def Run(Pattern, Table, IDColumn, Columns):
		#First, we need to run the pattern on the content
		Matches = re.findall(Pattern, Content)
		#Let's make our SQL statement. We use a tuple for columns so that we can create the right number of ? tokens
		SQL = "INSERT INTO "+Table+"(PageID,"+",".join(Columns)+") VALUES (?,"+("?,"*len(Columns))[:-1]+")"
		NewFields = HandleInserts(Matches, PageID, SQL)
		for Match in Matches:
			if Match[0] == "Date" or Match[0] == "Birthdate":
				HandleDate(PageID, Match[1])
		#Now we need the old fields for the HandleDupes
		Cursor.execute("SELECT "+IDColumn+" FROM "+Table+" WHERE PageID = ?", (PageID,))
		OldFields = Cursor.fetchall()
		HandleDupes(PageID, NewFields, OldFields, Table, IDColumn)
	#It's absolutely likely that there is a more elegant way to do this
	#But I like reducing the number of times I have to type the same thing.
	if Grimoire_Config.Enable_Markdown:
		Run(r'## ([^\n]+)([\w\W]+?)(?:\* \* \*|$)', "Fields", "FieldName", ("FieldName"," FieldContent"))
		Run(r'\*\*([\w\W]+?)\*\*:([\w\W]+?)(?:\||\r|\n)', "Fields", "FieldName", ("FieldName"," FieldContent"))
	if Grimoire_Config.Enable_Potential:
		SearchForLinks(Content)


#This function gets the timeline of all events in a book
def GetTimeline(Book):
	#This fetches a list of all Eras, their orders, and if they should be reversed
	Cursor.execute("SELECT EraName, EraOrder, Reversed FROM Dates WHERE PageID IN( SELECT PageID FROM Pages WHERE BookName = ?) GROUP BY EraOrder;", (Book,))
	Pages = Cursor.fetchall()
	Data = []
	for Era in Pages:
		#We create the SQL, and append DESC if it has to be reversed
		SQL = "SELECT * FROM Dates WHERE PageID IN( SELECT PageID FROM Pages WHERE BookName = ?) AND EraName = ? ORDER BY YEAR"
		if Era[2] == 1:
			SQL += " DESC"
		Cursor.execute(SQL, (Book, Era[0]))
		for Date in Cursor.fetchall():
			#We create the tuple with all the data needed in the timeline
			TmpDate = str(Date[1]) + Date[2]
			TmpName = FromID(Date[0]).split("/")[1]
			TmpOverview = None
			Type = GetType(Date[0])
			if "character" in Type.lower():
				TmpOverview = TmpName + " was born."
			elif "location" in Type.lower():
				TmpOverview = TmpName + " was founded."
			elif "event" in Type.lower():
				TmpOverview = GetOverview(Date[0])
			if TmpOverview is not None:
				Data.append((TmpDate, TmpName, TmpOverview))
	#We return the now-populated data array
	return Data

#This function handles inserts, deciding if a page should be updated or created
def HandleSubmit(Book, Page, Content, Tags):
	try:
		Data = GetPage(Book, Page)
		RValue = None
		if Data == None:
			#If there's no page data, create a new page
			RValue = NewPage(Book, Page, Content, Tags)
		else:
			#If there is page data, update a page
			RValue = UpdatePage(Data, Content, Tags)
		return RValue
	except Exception as E:
		Grimoire_Config.HandleErrMsg(E)


def HandleAppend(Book, Page, Append):
	try:
		Data = GetPage(Book, Page)
		if Data == None or len(Data) < 3:
			return HandleSubmit(Book, Page, Append, None)
		Content = Data[3] + """
	""" + Append
		RValue = UpdatePage(Data, Content, None)
		return RValue
	except Exception as E:
		Grimoire_Config.HandleErrMsg(E)

#This function grabs the latest changes logged in the or
def GetChanges():
	Cursor.execute("SELECT * FROM Changes LIMIT 10")
	return Cursor.fetchall()


def FieldsTagsReadout(Book):
	Cursor.execute("""SELECT Pages.PageName, Pages.BookName,
	GROUP_CONCAT(FieldName, ", "), GROUP_CONCAT(Tag, ", ")
	FROM Pages
	INNER JOIN Fields ON Pages.PageID = Fields.PageID
	INNER JOIN Tags ON Pages.PageID = Tags.PageID
	WHERE BookName = ? GROUP BY Pages.PageID;""", (Book, ))
	return Cursor.fetchall()

def RandoLink(Book):
	Cursor.execute("SELECT * FROM Linked WHERE Book = ? ORDER BY RANDOM() LIMIT 1", (Book,))
	return Cursor.fetchone()
