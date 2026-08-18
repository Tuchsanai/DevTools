INSERT INTO menus (code, name_th, price) VALUES
('latte',     'ลาเต้',       65.00),
('espresso',  'เอสเปรสโซ',  55.00),
('americano', 'อเมริกาโน',  50.00),
('mocha',     'มอคค่า',      70.00),
('matcha',    'มัทฉะลาเต้',  75.00),
('cocoa',     'โกโก้',       60.00);

INSERT INTO sales_stats (menu_code, cups, revenue) VALUES
('latte',0,0),('espresso',0,0),('americano',0,0),
('mocha',0,0),('matcha',0,0),('cocoa',0,0);
