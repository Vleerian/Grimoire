# Grimoire
A project I made in my spare time
* * *
## What is Grimoire?
So I really like Notebook.ai, but at the same time I'm a poor college student.
I also don't want to use data, and don't necessarily have my worldbuilding ideas while at a computer.
so I thought "what if I made a handy worldbuilding notebook thing that could run on a raspberry pi?"
Well my friends, many hours later, and you have a disasterous project of love, and terrible coding practices.

~~I promise I'll comment everything eventually~~

## How do I make this work?
You basically need to get [Sanic](https://github.com/channelcat/sanic) working. If you're on windows, you'll have to
disable UVLoop and UJson to develop. It works perfectly on Linux, can confirm. You'll also need [Markdown](https://python-markdown.github.io/)
because I wasn't in the mood to write the regex to get that all working properly. Why re-invent the wheel and all.

~~I may replace markdown in the future with some custom spaghetti code so I can drop a license.~~

## I have my dependencies, what now?
The database has to be initialized. I included the ddl to do so in CreateTables.sql. Once that's done, you start up
main.py and you're off to the races!

## How do I add pages?
On the topbar there is "New," you can add pages using that

## What's this book nonsense?
I thought it would be cool if you could have Book1/Derp and Book2/Derp exist without a name collision
I also wanted the URI to look pretty, so you get books. It also is handy if you are using this for something
not-worldbuilding related, because you can keep math separate from english.

compartmentalization!

## How do I make things look nice?
[Markdown!](https://daringfireball.net/projects/markdown/syntax#link)

## What are these glowing links that show up?
When you link to a non-existent internal page the grimoire considers it a 'potential' page.
It's basically saying "Heyo! You should give this place some love and attention."

## What license are you putting this under?
I'm going with the Copyright(c) Atagait Denral 2018 license. I wouldn't enforce any license I chose, and I have no
idea how any one I chose would interact with Markdown's or Sanic's, so I'm just steering clear of that for now.
If any of you legal types can advise, that'd be appreciated :D

## What does 'Zodivikh' mean?
It means mortal, and is generally used as a passive-aggressive way of saying you're better than someone else.
