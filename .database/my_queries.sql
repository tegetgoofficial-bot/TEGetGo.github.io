--database: c:\Users\armwi\Documents\Html\IN_SYD_Task_1_Flask_PWA_Template-main\.database\data_source.db
-- CREATE TABLE extension(
--     extID INTEGER NOT NULL PRIMARY KEY,
--     name TEXT NOT NULL, 
--     hyperlink TEXT NOT NULL,
--     about TEXT NOT NULL,
--     image TEXT NOT NULL,
--     language TEXT NOT NULL
-- );
-- INSERT INTO extension(extID,name,hyperlink,about,image,language) VALUES (1,"Live Server","https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer","Launch a development local Server with live reload feature for static & dynamic pages","https://ritwickdey.gallerycdn.vsassets.io/extensions/ritwickdey/liveserver/5.7.9/1661914858952/Microsoft.VisualStudio.Services.Icons.Default","HTML CSS JS");
-- INSERT INTO extension(extID,name,hyperlink,about,image,language) VALUES (2,"Render CR LF","https://marketplace.visualstudio.com/items?itemName=medo64.render-crlf","Displays the line ending symbol and optionally extra whitespace when 'Render whitespace' is turned on.","https://medo64.gallerycdn.vsassets.io/extensions/medo64/render-crlf/1.7.1/1689315206970/Microsoft.VisualStudio.Services.Icons.Default","#BASH");
-- INSERT INTO extension(extID,name,hyperlink,about,image,language) VALUES (3,"Start GIT BASH","https://marketplace.visualstudio.com/items?itemName=McCarter.start-git-bash","Adds a bash command to VSCode that allows you to start git-bash in the current workspace's root folder.","https://mccarter.gallerycdn.vsassets.io/extensions/mccarter/start-git-bash/1.2.1/1499505567572/Microsoft.VisualStudio.Services.Icons.Default","#BASH");
-- INSERT INTO extension(extID,name,hyperlink,about,image,language) VALUES (4,"SQLite3 Editor","https://marketplace.visualstudio.com/items?itemName=yy0931.vscode-sqlite3-editor","Edit SQLite3 files like you would in spreadsheet applications.","https://yy0931.gallerycdn.vsassets.io/extensions/yy0931/vscode-sqlite3-editor/1.0.85/1690893830873/Microsoft.VisualStudio.Services.Icons.Default","SQL");
-- SELECT * FROM extension;
-- SELECT * FROM extension WHERE language LIKE '#BASH';

-- CREATE TABLE CATEGORIES(
--     bagID INTEGER NOT NULL PRIMARY KEY,
--     bagType TEXT NOT NULL
-- )

-- CREATE TABLE ITEM(
--     bagID INTEGER NOT NULL PRIMARY KEY,
--     name TEXT NOT NULL,
--     cost integer NOT NULL,
--     bagDescription TEXT NOT NULL,
--     bagType TEXT NOT NULL
--     FOREIGN KEY(bagID) REFERENCES CETEGORIES(bagID)

-- )

DROP TABLE LOGIN_DETAIL;
DROP TABLE PASSWORD;
DROP TABLE USER;