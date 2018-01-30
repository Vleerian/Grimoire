CREATE TABLE Pages (
    PageID INTEGER PRIMARY KEY AUTOINCREMENT,
    PageName TEXT,
    BookName TEXT
);

CREATE TABLE Content (
    PageID INTEGER,
    Valid INTEGER,
    Body TEXT,
    FOREIGN KEY(PageID) REFERENCES Pages(PageID)
);

CREATE TABLE `Changes` (
    `Timestamp` TEXT,
    `PageID` INTEGER,
    `OriginalID` INTEGER,
    `NewID` INTEGER,
    `NameNote` TEXT,
    `BookNote` TEXT ,
    FOREIGN KEY(`PageID`) REFERENCES `Pages`(`PageID`)
    FOREIGN KEY(`OriginalID`) REFERENCES `Content`(`ID`)
    FOREIGN KEY(`NewID`) REFERENCES `Content`(`ID`)
);

CREATE TABLE `Fields` (
	`PageID`	INTEGER,
	`FieldName`	TEXT NOT NULL,
	`FieldContent`	TEXT NOT NULL,
    FOREIGN KEY(`PageID`) REFERENCES `Pages`(`PageID`)
    UNIQUE (PageID, FieldName)
);

CREATE TABLE `Tags` (
	`PageID`	INTEGER,
	`Tag`	TEXT,
    FOREIGN KEY(`PageID`) REFERENCES `Pages`(`PageID`)
    UNIQUE (PageID, Tag)
);

CREATE TABLE `Linked` (
	`Name`	TEXT,
	`Book`	TEXT,
    UNIQUE (Name, Book)
);

CREATE TRIGGER RemoveLinked
AFTER INSERT ON Pages
WHEN EXISTS (SELECT * FROM Linked WHERE NEW.PageName = Name AND NEW.BookName = Book)
BEGIN
DELETE FROM Linked WHERE NEW.PageName = Name AND NEW.BookName = Book;
END;

CREATE TRIGGER PreventLinkingExitant
AFTER INSERT ON Linked
WHEN EXISTS (SELECT * FROM Pages WHERE New.Page = PageName AND NEW.Book = BookName)
BEGIN
DELETE FROM Linked WHERE PageName = NEW.Name AND BookName = NEW.Book;
END;

CREATE TRIGGER new_page
AFTER INSERT ON Pages
BEGIN
INSERT INTO Changes(Timestamp, PageID, NameNote)
VALUES (datetime(1092941466, 'unixepoch', 'localtime'), NEW.PageID, NEW.PageID || " now exists.");
END;

CREATE TRIGGER update_changes
AFTER INSERT ON Content
WHEN EXISTS (SELECT COUNT(*) FROM Content WHERE PageID = NEW.PageID ORDER BY ID DESC LIMIT 1)
BEGIN
INSERT INTO Changes(Timestamp, PageID, OriginalID, NewID)
VALUES (datetime(1092941466, 'unixepoch', 'localtime'), NEW.PageID, NEW.ID, (SELECT ID FROM Content WHERE PageID = NEW.PageID LIMIT 1 OFFSET 1));
END;

CREATE TRIGGER name_changes
AFTER UPDATE ON Pages
WHEN OLD.PageName <> NEW.PageName OR OLD.BookName <> NEW.BookName
BEGIN
INSERT INTO Changes(Timestamp, PageID, NameNote, BookNote)
VALUES (datetime(1092941466, 'unixepoch', 'localtime'), NEW.PageID, OLD.PageName || " now " || NEW.PageName, OLD.BookName || " now " || NEW.BookName);
END;

CREATE TRIGGER Invalidate_Content
BEFORE INSERT ON Content
BEGIN
UPDATE Content SET Valid = 0 WHERE PageID = NEW.PageID;
END;

CREATE TRIGGER UpdateFields
BEFORE INSERT ON Fields
WHEN EXISTS (SELECT * FROM Fields WHERE PageID = NEW.PageID AND FieldName = NEW.FieldName)
BEGIN
UPDATE Fields SET FieldContent = NEW.FieldContent WHERE PageID = NEW.PageID AND FieldName = NEW.FieldName;
END;
