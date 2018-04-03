# -*- coding: utf-8 -*-
import asyncio
from sanic import Sanic
from sanic import response
from sanic.response import text, redirect
from signal import signal, SIGINT
from DBHandler import *
from PromptHandler import *

#Create the app and define static content
app = Sanic()
app.static('/Templates', './Templates')
app.static('/Assets', './Assets')


#Loadtemplate command. Yes, I should use a library, but this also
#Allows me to change an HTML file, refresh, and see the changes.
#I'll likely swap it out in the future, if I can find a good reason.
def loadTemplate(Template):
	header = open("Templates/header.html", "r").read()
	index = open("Templates/"+Template+".html", "r").read()
	footer = open("Templates/footer.html", "r").read()
	return header + index + footer


#Index page, we don't need to do much here other than give general
#information. It also provides recent changes, because why not.
@app.route("/")
async def index(request):
	resp = loadTemplate("index")
	Data = GetChanges()
	Changes = ""
	for Change in Data:
		Changes += Change[0] + ": "
		Destination = FromID(Change[1])
		if isinstance(Change[2], int):
			Changes += '<a href="/read/' + Destination + '">' + Destination.split("/")[1] + "</a> was edited."
		elif "now exists" in Change[4]:
			Changes += '<a href="/read/' + Destination + '">' + Destination.split("/")[1] + "</a> was created."
		else:
			Changes += Change[5].split(" now ")[0]+"'s page " + Change[4].split(" now ")[0] + ' was moved <a href="/read'
			Changes += Change[5].split(" now ")[-1] + "/" + Change[4].split(" now ")[-1] +'">here</a>.'
		Changes += "<br>"
	resp = resp.replace("$CHANGES", Changes)
	return response.html(resp, status=200)


#Newpage. Does little but serve a form to create new pages.
@app.route("/newPage", methods=['GET', 'POST'])
async def book(request):
	resp = loadTemplate("newpage")
	if "Edit" in request.form:
		resp = resp.replace("$BOOK", request.form['Book'][0]).replace("$PAGE", request.form['Page'][0])
		resp = resp.replace("$CONTENT", request.form['Content'][0])
		try:
			resp = resp.replace("$TAGS", request.form['Tags'][0])
		except Exception:
			resp = resp.replace("$TAGS", "Add a tag, Zodivikh")
	else:
		resp = resp.replace("$BOOK", "").replace("$PAGE", "").replace("$CONTENT", "").replace("$TAGS", "")
	return response.html(resp, status=200)


#Submit, it's the heavy lifting part of newpage that Handles
#actually committing pages to the database.
@app.route("/submit", methods=['POST'])
async def submit(request):
	if "NEW" in request.form:
		resp = HandleSubmit(request.form['Book'][0], request.form['Page'][0],
						request.form['Content'][0], request.form['Tags'][0])
		if resp == True:
			return redirect("/read/"+request.form['Book'][0]+"/"+request.form['Page'][0])
		else:
			return response.html(loadTemplate("SubmitError"), status=404)
	elif "APPEND" in request.form:
		resp = HandleAppend(request.form['Book'][0], request.form['Page'][0], request.form['Append'][0])
		if resp == True:
			return redirect("/read/"+request.form['Book'][0]+"/"+request.form['Page'][0])
		else:
			return response.html(loadTemplate("SubmitError"), status=404)
	else:
		return redirect("/")


#Book, this is the menu that lets you see all the pabes in a book.
@app.route("/read/<book>")
async def book(request, book, api="false"):
	book = urllib.parse.unquote(book)
	Data = GetBook(book)
	if Data == None:
		return response.html(loadTemplate("NoPage"), status=404)
	Pages = ""
	for Page in Data:
		Pages += '<a href="/read/'+book+"/"+Page[1]+'">'+Page[1]+"</a><br>"
	Data = GetPotentialBook(book)
	for Page in Data:
		Pages += '<a class="glow" href="/read/'+book+"/"+Page[1]+'">'+Page[1]+"</a><br>"
	Template = loadTemplate("list")
	resp = Template.replace("$TITLE", book).replace("$ITEMS", Pages)

	Prompt = Prompts().CreatePrompt(book)
	if not Prompt == None:
		resp = resp.replace("$PROMPT", Prompt)
	else:
		resp = resp.replace("$PROMPT", "")

	return response.html(resp, status=200)


#Potential books are books that are linked elsewhere, but have no actual pages.
@app.route("/potential/<book>")
async def potentialbook(request, book, api="false"):
	book = urllib.parse.unquote(book)
	Data = GetPotentialBook(book)
	if Data == None:
		return response.html(loadTemplate("NoPage"), status=404)
	Pages = ""
	for Page in Data:
		Pages += '<a class="glow" href="/read/'+book+"/"+Page[1]+'">'+Page[1]+"</a><br>"
	Template = loadTemplate("list")
	resp = Template.replace("$TITLE", '<span class="glow">'+book+'</span>').replace("$ITEMS", Pages)
	Prompt = Prompts().CreatePrompt(book)
	if Prompt is not None:
		resp = resp.replace("$PROMPT", Prompt)
	else:
		resp = resp.replace("$PROMPT", "")

	return response.html(resp, status=200)


#A list of all the books
@app.route("/books")
async def books(request):
	Data = GetBooks()
	if Data == None:
		return response.text("There's a serious problem, Zodivikh. Be sure you look at that 'console' of yours and fix it.", status=404)
	Books = ""
	for Book in Data:
		Books += '<a href="/read/'+Book[0]+'">'+Book[0]+"</a><br>"
	Data = GetPotentialBooks()
	if Data == None:
		pass
	else:
		for Book in Data:
			Books += '<a class="glow" href="/potential/'+Book[0]+'">'+Book[0]+"</a><br>"
	Template = loadTemplate("list")
	resp = Template.replace("$TITLE", "The Library").replace("$ITEMS", Books)
	resp = resp.replace("$PROMPT", "")
	return response.html(resp, status=200)


#A page
@app.route("/read/<book>/<page>")
async def page(request, book, page):
	book = urllib.parse.unquote(book)
	page = urllib.parse.unquote(page)
	Data = GetPage(book, page)
	if Data == None:
		resp = loadTemplate("NoPage").replace("$BOOK", book).replace("$PAGE", page)
		return response.html(resp, status=404)
	Template = loadTemplate("page")

	resp = Template.replace("$PAGE", Data[1]).replace("$BOOK",
	Data[2]).replace("$CONTENT", Data[3])
	try:
		resp = resp.replace("$TAGS", Data[4])
	except Exception:
		resp = resp.replace("$TAGS", "").replace("hidden>$MESSAGE", ">This page is missing a tag, Zodivikh.")
	return response.html(resp, status=200)


@app.route("/timeline/<book>")
async def timeline(request, book):
	Timeline = GetTimeline(book)
	if Timeline is None or len(Timeline) == 0:
		resp = loadTemplate("None").replace("$CONTENT", "Your timeline is empty, Zodivikh.")
		return response.html(resp, status=200)
	Elements = ""
	ElementTemplate = open("Templates/timelineElement.html", "r").read()
	ElementTemplateInverse = open("Templates/timelineElementInverse.html", "r").read()
	Inverse = 0
	for Date in Timeline:
		if Inverse == 0:
			Elements += ElementTemplate.replace("$ITEMNAME", Date[0] + " " + Date[1]).replace("$ITEMBODY", Date[2])
			Inverse = 1
		else:
			Elements += ElementTemplateInverse.replace("$ITEMNAME", Date[0] + " " + Date[1]).replace("$ITEMBODY", Date[2])
			Inverse = 0
	resp = loadTemplate("timeline")
	resp = resp.replace("$TIMELINEBODY", Elements).replace("$BOOK", book)
	return response.html(resp, status=200)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=Grimoire_Config.Port)
