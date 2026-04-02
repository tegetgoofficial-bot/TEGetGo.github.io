-- 1. Create CATEGORIES Table
CREATE TABLE CATEGORIES (
    "Category_ID" BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "itemType" TEXT NOT NULL,
    "icon" TEXT,
    "description" TEXT,
    "Main_Cat" TEXT
);

-- 2. Create ITEM Table
CREATE TABLE ITEM (
    "Item_ID" BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "name" TEXT NOT NULL,
    "cost" INTEGER NOT NULL,
    "itemDesc" TEXT NOT NULL,
    "image" TEXT NOT NULL,
    "clickCount" INTEGER DEFAULT 0,
    "itemLink" TEXT
);

-- 3. Create ITEM_CATEGORIES (Joining Table)
CREATE TABLE ITEM_CATEGORIES (
    "Item_ID" BIGINT REFERENCES ITEM("Item_ID") ON DELETE CASCADE,
    "Category_ID" BIGINT REFERENCES CATEGORIES("Category_ID") ON DELETE CASCADE,
    PRIMARY KEY ("Item_ID", "Category_ID")
);

-- 4. Create MAIN_CATEGORIES Table
CREATE TABLE MAIN_CATEGORIES (
    "ID" BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "CATEGORIES" TEXT NOT NULL
);

-- INSERT DATA
INSERT INTO CATEGORIES ("itemType", "icon", "description") VALUES
('Books','📚','For Books'),
('Games','🎮','For Games'),
('Gears','⚙️','For Gears'),
('Assets','🛠️','For Assets'),
('WebSites','🗒️','For Webpages'),
('Delivery Website','📦','Delivery Website'),
('Cool Stuff','🎆','stuff'),
('Random Stuff','🎲','Random');

INSERT INTO ITEM ("name", "cost", "itemDesc", "image", "clickCount", "itemLink") VALUES
('Fashion Bag', 100, 'A nice Fashion Bag', 'https://bing.com', 1, 'https://google.com'),
('Normal Bag', 50, 'A nice normal Bag', 'https://gstatic.com', 2, 'https://google.com'),
('Crossbody Bag', 100, 'Nordace Siena Pro Crossbody Bag', 'https://nordace.com', 27, 'https://google.com'),
('Smart Bag', 170, 'Built for Daily Use. Ready for Every Journey.', 'https://nordace.com', 386, 'https://google.com'),
('Tote Bag', 148, 'The ultimate travel tote for an effortless journey.', 'https://nordace.com', 3, 'https://google.com'),
('Laptop Bag', 50, 'Slim Durable, Enti theft protection and more', 'https://bing.com', 10000, 'https://google.com');

INSERT INTO MAIN_CATEGORIES ("CATEGORIES") VALUES
('tech'),
('gameDev'),
('books');
