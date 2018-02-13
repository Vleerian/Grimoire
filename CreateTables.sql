CREATE TABLE Pages (
    `PageID` INTEGER PRIMARY KEY AUTOINCREMENT,
    `PageName` TEXT NOT NULL,
    `BookName` TEXT NOT NULL
);

CREATE TABLE Content (
    `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
    `PageID` INTEGER NOT NULL,
    `Valid` INTEGER NOT NULL,
    `Body` TEXT NOT NULL,
    FOREIGN KEY(PageID) REFERENCES Pages(PageID)
);

CREATE TABLE `Changes` (
    `Timestamp` TEXT NOT NULL,
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
    `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
	`PageID`	INTEGER NOT NULL,
	`FieldName`	TEXT NOT NULL,
	`FieldContent`	TEXT NOT NULL,
    FOREIGN KEY(`PageID`) REFERENCES `Pages`(`PageID`)
    UNIQUE (PageID, FieldName)
);

CREATE TABLE `Tags` (
	`PageID`	INTEGER NOT NULL,
	`Tag`	TEXT NOT NULL,
    FOREIGN KEY(`PageID`) REFERENCES `Pages`(`PageID`)
    UNIQUE (PageID, Tag)
);

CREATE TABLE `Linked` (
	`Name`	TEXT NOT NULL,
	`Book`	TEXT NOT NULL,
    UNIQUE (Name, Book)
);

CREATE TABLE `Dates` (
	`PageID`	INTEGER NOT NULL,
	`Year`	INTEGER NOT NULL,
	`EraName`	INTEGER NOT NULL,
	`EraOrder`	INTEGER NOT NULL,
	`Reversed`	INTEGER NOT NULL,
    FOREIGN KEY(`PageID`) REFERENCES `Pages`(`PageID`),
    UNIQUE (PageID)
);

CREATE TRIGGER RemoveLinked
AFTER INSERT ON Pages
WHEN EXISTS (SELECT * FROM Linked WHERE NEW.PageName = Name AND NEW.BookName = Book)
BEGIN
DELETE FROM Linked WHERE NEW.PageName = Name AND NEW.BookName = Book;
END;

CREATE TRIGGER PreventLinkingExitant
AFTER INSERT ON Linked
BEGIN
DELETE FROM Linked WHERE Name IN (SELECT PageName FROM Pages);
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
