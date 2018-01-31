# -*- coding: utf-8 -*-
import asyncio
from sanic import Sanic
from sanic import response
from sanic.response import text, redirect
from signal import signal, SIGINT
from DBHandler import *
from MarkupHandler import *
from PromptHandler import *

app = Sanic("sanic_jinja2_render")
app.static('/Templates', './Templates')
app.static('/Assets', './Assets')

def loadTemplate(Template):
	header = open("Templates/header.html", "r").read()
	index = open("Templates/"+Template+".html", "r").read()
	footer = open("Templates/footer.html", "r").read()
	return header + index + footer


@app.route("/")
async def index(request):
	resp = loadTemplate("index")
	Data = GetChanges()
	Changes = ""
	for Change in Data:
		Changes += Change[0] + ": "
		Destination = FromID(Change[1])
		if isinstance(Change[2], int):
			Changes += '<a href="/' + Destination + '">' + Destination.split("/")[1] + "</a> was edited."
		elif "now exists" in Change[4]:
			Changes += '<a href="/' + Destination + '">' + Destination.split("/")[1] + "</a> was created."
		else:
			Changes += Change[5].split(" now ")[0]+"'s page " + Change[4].split(" now ")[0] + ' was moved <a href="'
			Changes += Change[5].split(" now ")[-1] + "/" + Change[4].split(" now ")[-1] +'">here</a>.'
		Changes += "<br>"
	resp = resp.replace("$CHANGES", Changes)
	return response.html(resp, status=200)


@app.route("/newPage", methods=['GET', 'POST'])
async def book(request):
	resp = loadTemplate("newpage")
	if "Edit" in request.form:
		resp = resp.replace("$BOOK", request.form['Book'][0]).replace("$PAGE", request.form['Page'][0]).replace("$CONTENT", request.form['Content'][0])
	else:
		resp = resp.replace("$BOOK", "").replace("$PAGE", "").replace("$CONTENT", "")
	return response.html(resp, status=200)


@app.route("/submit", methods=['POST'])
async def index(request):
	if "NEW" in request.form:
		resp = HandleSubmit(request.form['Book'][0], request.form['Page'][0], request.form['Content'][0])
		if resp == True:
			return redirect("/"+request.form['Book'][0]+"/"+request.form['Page'][0])
		else:
			return response.html(loadTemplate("SubmitError"), status=404)
	elif "APPEND" in request.form:
		resp = HandleAppend(request.form['Book'][0], request.form['Page'][0], request.form['Append'][0])
		if resp == True:
			return redirect("/"+request.form['Book'][0]+"/"+request.form['Page'][0])
		else:
			return response.html(loadTemplate("SubmitError"), status=404)
	else:
		return redirect("/")


@app.route("/<book>")
async def book(request, book, api="false"):
	book = urllib.parse.unquote(book)
	Data = GetBook(book)
	if Data == None:
		return response.html(loadTemplate("NoPage"), status=404)
	Pages = ""
	for Page in Data:
		Pages += '<a href="/'+book+"/"+Page[1]+'">'+Page[1]+"</a><br>"
	Template = loadTemplate("list")
	resp = Template.replace("$TITLE", book).replace("$ITEMS", Pages)

	Prompt = Prompts().CreatePrompt(book)
	if not Prompt == None:
		resp = resp.replace("$PROMPT", Prompt)
	else:
		resp = resp.replace("$PROMPT", "")

	return response.html(resp, status=200)


@app.route("/potential/<book>")
async def book(request, book, api="false"):
	book = urllib.parse.unquote(book)
	Data = GetPotentialBook(book)
	if Data == None:
		return response.html(loadTemplate("NoPage"), status=404)
	Pages = ""
	for Page in Data:
		Pages += '<a class="glow" href="/'+book+"/"+Page[1]+'">'+Page[1]+"</a><br>"
	Template = loadTemplate("list")
	resp = Template.replace("$TITLE", '<span class="glow">'+book+'</span>').replace("$ITEMS", Pages)

	Prompt = Prompts().CreatePrompt(book)
	if not Prompt == None:
		resp = resp.replace("$PROMPT", Prompt)
	else:
		resp = resp.replace("$PROMPT", "")

	return response.html(resp, status=200)


@app.route("/books")
async def books(request):
	Data = GetBooks()
	if Data == None:
		return response.text("There's a serious problem, Zodivikh. Be sure you look at that 'console' of yours and fix it.", status=404)
	Books = ""
	for Book in Data:
		Books += '<a href="/'+Book[0]+'">'+Book[0]+"</a><br>"
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


@app.route("/<book>/<page>")
async def page(request, book, page):
	book = urllib.parse.unquote(book)
	page = urllib.parse.unquote(page)
	Data = GetPage(book, page)
	if Data == None:
		resp = loadTemplate("NoPage").replace("$BOOK", book).replace("$PAGE", page)
		return response.html(resp, status=404)
	Template = loadTemplate("page")

	resp = Template.replace("$TITLE", Data[1]).replace("$BOOK",
	Data[2]).replace("$CONTENT", Markup(Data[3])).replace("$RAWCONTENT", Data[3])
	return response.html(resp, status=200)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000)
