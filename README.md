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
disable UVLoop and UJson to develop. It works perfectly on Linux just by using pip, can confirm.

## I have my dependencies, what now?
The database is already configured, but if you want to be sure, I included the DDL in CreateTables.sql.
Otherwise, open config.py and make sure everything is to your liking.

## How do I add pages?
On the topbar there is "New," you can add pages using that

## What's this book nonsense?
I thought it would be cool if you could have Book1/Derp and Book2/Derp exist without a name collision
I also wanted the URI to look pretty, so you get books. It also is handy if you are using this for something
not-worldbuilding related, because you can keep math separate from english.

compartmentalization!

## How do I make things look nice?
Grimoire uses a WYSIWYG editor named [Trumboyg](https://github.com/Alex-D/Trumbowyg). If you can make something
look pretty with word, you should be able to make something look pretty in Grimoire.

## What are these glowing links that show up?
When you link to a non-existent internal page the grimoire considers it a 'potential' page.
It's basically saying "Heyo! You should give this place some love and attention."

## What does 'Zodivikh' mean?
It means mortal, and is generally used as a passive-aggressive way of saying you're better than someone else.

#What's this spaghetti nonsense with template loading?
I couldnt' get jinja2 to work. If you want to make a prettier template-loader, go for it!

## What is your policy on contribution?
I honestly have no idea how a pull request works, so if someone teaches that to me, I'll write something more
sensible. For now, if you make a change you want included, lemme know and I'll work on figuring out how that works.
