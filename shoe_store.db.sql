BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "categories" (
	"id_category"	INTEGER NOT NULL UNIQUE,
	"category_name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id_category" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "manufacturers" (
	"id_manufacturer"	INTEGER NOT NULL UNIQUE,
	"manufacturer_name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id_manufacturer" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "orders" (
	"id_order"	INTEGER NOT NULL UNIQUE,
	"order_articles"	TEXT NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"status_id"	INTEGER NOT NULL,
	"pickup_point_id"	INTEGER NOT NULL,
	"code"	INTEGER NOT NULL,
	"date_order"	date NOT NULL,
	"date_delivery"	date NOT NULL,
	PRIMARY KEY("id_order" AUTOINCREMENT),
	FOREIGN KEY("user_id") REFERENCES "users"("id_user"),
	FOREIGN KEY("status_id") REFERENCES "statuses"("id_status"),
	FOREIGN KEY("pickup_point_id") REFERENCES "pickup_points"("id_pickup_point")
);
CREATE TABLE IF NOT EXISTS "pickup_points" (
	"id_pickup_point"	INTEGER NOT NULL UNIQUE,
	"pickup_point_address"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id_pickup_point" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "products" (
	"id_product"	INTEGER NOT NULL UNIQUE,
	"sku"	TEXT NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"description"	TEXT NOT NULL,
	"price"	REAL NOT NULL,
	"unit"	TEXT NOT NULL,
	"category_id"	INTEGER NOT NULL,
	"manufacturer_id"	INTEGER NOT NULL,
	"supplier_id"	INTEGER NOT NULL,
	"quantity"	INTEGER NOT NULL,
	"discount"	INTEGER NOT NULL,
	"photo_path"	TEXT,
	PRIMARY KEY("id_product" AUTOINCREMENT),
	FOREIGN KEY("category_id") REFERENCES "categories"("id_category"),
	FOREIGN KEY("manufacturer_id") REFERENCES "manufacturers"("id_manufacturer"),
	FOREIGN KEY("supplier_id") REFERENCES "suppliers"("id_supplier")
);
CREATE TABLE IF NOT EXISTS "roles" (
	"id_role"	INTEGER NOT NULL UNIQUE,
	"role_name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id_role" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "statuses" (
	"id_status"	INTEGER NOT NULL UNIQUE,
	"status_name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id_status" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "suppliers" (
	"id_supplier"	INTEGER NOT NULL UNIQUE,
	"supplier_name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id_supplier" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "users" (
	"id_user"	INTEGER NOT NULL UNIQUE,
	"role_id"	INTEGER NOT NULL,
	"fio"	TEXT NOT NULL,
	"login"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	PRIMARY KEY("id_user" AUTOINCREMENT),
	FOREIGN KEY("role_id") REFERENCES "roles"("id_role")
);
INSERT INTO "categories" VALUES (1,'Женская обувь');
INSERT INTO "categories" VALUES (2,'Мужская обувь');
INSERT INTO "manufacturers" VALUES (1,'Kari');
INSERT INTO "manufacturers" VALUES (2,'Marco Tozzi');
INSERT INTO "manufacturers" VALUES (3,'Рос');
INSERT INTO "manufacturers" VALUES (4,'Rieker');
INSERT INTO "manufacturers" VALUES (5,'Alessio Nesca');
INSERT INTO "manufacturers" VALUES (6,'CROSBY');
INSERT INTO "orders" VALUES (1,'А112Т4, 2, F635R4, 2',4,1,1,901,'2025-02-27','2025-04-20');
INSERT INTO "orders" VALUES (2,'H782T5, 1, G783F5, 1',1,1,11,902,'2022-09-28','2025-04-21');
INSERT INTO "orders" VALUES (3,'J384T6, 10, D572U8, 10',2,1,2,903,'2025-03-21','2025-04-22');
INSERT INTO "orders" VALUES (4,'F572H7, 5, D329H3, 4',3,1,11,904,'2025-02-20','2025-04-23');
INSERT INTO "orders" VALUES (5,'А112Т4, 2, F635R4, 2',4,1,2,905,'2025-03-17','2025-04-24');
INSERT INTO "orders" VALUES (6,'H782T5, 1, G783F5, 1',1,1,15,906,'2025-03-01','2025-04-25');
INSERT INTO "orders" VALUES (7,'J384T6, 10, D572U8, 10',2,1,3,907,'2025-02-28','2025-04-26');
INSERT INTO "orders" VALUES (8,'F572H7, 5, D329H3, 4',3,2,19,908,'2025-03-31','2025-04-27');
INSERT INTO "orders" VALUES (9,'B320R5, 5, G432E4, 1',4,2,5,909,'2025-04-02','2025-04-28');
INSERT INTO "orders" VALUES (10,'S213E3, 5, E482R4, 5',4,2,19,910,'2025-04-03','2025-04-29');
INSERT INTO "pickup_points" VALUES (1,'420151, г. Лесной, ул. Вишневая, 32');
INSERT INTO "pickup_points" VALUES (2,'125061, г. Лесной, ул. Подгорная, 8');
INSERT INTO "pickup_points" VALUES (3,'630370, г. Лесной, ул. Шоссейная, 24');
INSERT INTO "pickup_points" VALUES (4,'400562, г. Лесной, ул. Зеленая, 32');
INSERT INTO "pickup_points" VALUES (5,'614510, г. Лесной, ул. Маяковского, 47');
INSERT INTO "pickup_points" VALUES (6,'410542, г. Лесной, ул. Светлая, 46');
INSERT INTO "pickup_points" VALUES (7,'620839, г. Лесной, ул. Цветочная, 8');
INSERT INTO "pickup_points" VALUES (8,'443890, г. Лесной, ул. Коммунистическая, 1');
INSERT INTO "pickup_points" VALUES (9,'603379, г. Лесной, ул. Спортивная, 46');
INSERT INTO "pickup_points" VALUES (10,'603721, г. Лесной, ул. Гоголя, 41');
INSERT INTO "pickup_points" VALUES (11,'410172, г. Лесной, ул. Северная, 13');
INSERT INTO "pickup_points" VALUES (12,'614611, г. Лесной, ул. Молодежная, 50');
INSERT INTO "pickup_points" VALUES (13,'454311, г.Лесной, ул. Новая, 19');
INSERT INTO "pickup_points" VALUES (14,'660007, г.Лесной, ул. Октябрьская, 19');
INSERT INTO "pickup_points" VALUES (15,'603036, г. Лесной, ул. Садовая, 4');
INSERT INTO "pickup_points" VALUES (16,'394060, г.Лесной, ул. Фрунзе, 43');
INSERT INTO "pickup_points" VALUES (17,'410661, г. Лесной, ул. Школьная, 50');
INSERT INTO "pickup_points" VALUES (18,'625590, г. Лесной, ул. Коммунистическая, 20');
INSERT INTO "pickup_points" VALUES (19,'625683, г. Лесной, ул. 8 Марта');
INSERT INTO "pickup_points" VALUES (20,'450983, г.Лесной, ул. Комсомольская, 26');
INSERT INTO "pickup_points" VALUES (21,'394782, г. Лесной, ул. Чехова, 3');
INSERT INTO "pickup_points" VALUES (22,'603002, г. Лесной, ул. Дзержинского, 28');
INSERT INTO "pickup_points" VALUES (23,'450558, г. Лесной, ул. Набережная, 30');
INSERT INTO "pickup_points" VALUES (24,'344288, г. Лесной, ул. Чехова, 1');
INSERT INTO "pickup_points" VALUES (25,'614164, г.Лесной,  ул. Степная, 30');
INSERT INTO "pickup_points" VALUES (26,'394242, г. Лесной, ул. Коммунистическая, 43');
INSERT INTO "pickup_points" VALUES (27,'660540, г. Лесной, ул. Солнечная, 25');
INSERT INTO "pickup_points" VALUES (28,'125837, г. Лесной, ул. Шоссейная, 40');
INSERT INTO "pickup_points" VALUES (29,'125703, г. Лесной, ул. Партизанская, 49');
INSERT INTO "pickup_points" VALUES (30,'625283, г. Лесной, ул. Победы, 46');
INSERT INTO "pickup_points" VALUES (31,'614753, г. Лесной, ул. Полевая, 35');
INSERT INTO "pickup_points" VALUES (32,'426030, г. Лесной, ул. Маяковского, 44');
INSERT INTO "pickup_points" VALUES (33,'450375, г. Лесной ул. Клубная, 44');
INSERT INTO "pickup_points" VALUES (34,'625560, г. Лесной, ул. Некрасова, 12');
INSERT INTO "pickup_points" VALUES (35,'630201, г. Лесной, ул. Комсомольская, 17');
INSERT INTO "pickup_points" VALUES (36,'190949, г. Лесной, ул. Мичурина, 26');
INSERT INTO "products" VALUES (1,'А112Т4','Ботинки','Женские Ботинки демисезонные kari',4990.0,'шт.',1,1,1,6,3,'1.jpg');
INSERT INTO "products" VALUES (2,'F635R4','Ботинки','Ботинки Marco Tozzi женские демисезонные, размер 39, цвет бежевый',3244.0,'шт.',1,2,2,13,2,'2.jpg');
INSERT INTO "products" VALUES (3,'H782T5','Туфли','Туфли kari мужские классика MYZ21AW-450A, размер 43, цвет: черный',4499.0,'шт.',2,1,1,5,4,'3.jpg');
INSERT INTO "products" VALUES (4,'G783F5','Ботинки','Мужские ботинки Рос-Обувь кожаные с натуральным мехом',5900.0,'шт.',2,3,1,8,2,'4.jpg');
INSERT INTO "products" VALUES (5,'J384T6','Ботинки','B3430/14 Полуботинки мужские Rieker',3800.0,'шт.',2,4,2,16,2,'5.jpg');
INSERT INTO "products" VALUES (6,'D572U8','Кроссовки','129615-4 Кроссовки мужские',4100.0,'шт.',2,3,2,6,3,'6.jpg');
INSERT INTO "products" VALUES (7,'F572H7','Туфли','Туфли Marco Tozzi женские летние, размер 39, цвет черный',2700.0,'шт.',1,2,1,14,2,'7.jpg');
INSERT INTO "products" VALUES (8,'D329H3','Полуботинки','Полуботинки Alessio Nesca женские 3-30797-47, размер 37, цвет: бордовый',1890.0,'шт.',1,5,2,4,4,'8.jpg');
INSERT INTO "products" VALUES (9,'B320R5','Туфли','Туфли Rieker женские демисезонные, размер 41, цвет коричневый',4300.0,'шт.',1,4,1,6,2,'9.jpg');
INSERT INTO "products" VALUES (10,'G432E4','Туфли','Туфли kari женские TR-YR-413017, размер 37, цвет: черный',2800.0,'шт.',1,1,1,15,3,'10.jpg');
INSERT INTO "products" VALUES (11,'S213E3','Полуботинки','407700/01-01 Полуботинки мужские CROSBY',2156.0,'шт.',2,6,2,6,3,NULL);
INSERT INTO "products" VALUES (12,'E482R4','Полуботинки','Полуботинки kari женские MYZ20S-149, размер 41, цвет: черный',1800.0,'шт.',1,1,1,14,2,NULL);
INSERT INTO "products" VALUES (13,'S634B5','Кеды','Кеды Caprice мужские демисезонные, размер 42, цвет черный',5500.0,'шт.',2,6,2,0,3,NULL);
INSERT INTO "products" VALUES (14,'K345R4','Полуботинки','407700/01-02 Полуботинки мужские CROSBY',2100.0,'шт.',2,6,2,3,2,NULL);
INSERT INTO "products" VALUES (15,'O754F4','Туфли','Туфли женские демисезонные Rieker артикул 55073-68/37',5400.0,'шт.',1,4,2,18,4,NULL);
INSERT INTO "products" VALUES (16,'G531F4','Ботинки','Ботинки женские зимние ROMER арт. 893167-01 Черный',6600.0,'шт.',1,1,1,9,12,NULL);
INSERT INTO "products" VALUES (17,'J542F5','Тапочки','Тапочки мужские Арт.70701-55-67син р.41',500.0,'шт.',2,1,1,0,13,NULL);
INSERT INTO "products" VALUES (18,'B431R5','Ботинки','Мужские кожаные ботинки/мужские ботинки',2700.0,'шт.',2,4,2,5,2,NULL);
INSERT INTO "products" VALUES (19,'P764G4','Туфли','Туфли женские, ARGO, размер 38',6800.0,'шт.',1,6,1,15,15,NULL);
INSERT INTO "products" VALUES (20,'C436G5','Ботинки','Ботинки женские, ARGO, размер 40',10200.0,'шт.',1,5,1,9,15,NULL);
INSERT INTO "products" VALUES (21,'F427R5','Ботинки','Ботинки на молнии с декоративной пряжкой FRAU',11800.0,'шт.',1,4,2,11,15,NULL);
INSERT INTO "products" VALUES (22,'N457T5','Полуботинки','Полуботинки Ботинки черные зимние, мех',4600.0,'шт.',1,6,1,13,3,NULL);
INSERT INTO "products" VALUES (23,'D364R4','Туфли','Туфли Luiza Belly женские Kate-lazo черные из натуральной замши',12400.0,'шт.',1,1,1,5,16,NULL);
INSERT INTO "products" VALUES (24,'S326R5','Тапочки','Мужские кожаные тапочки "Профиль С.Дали" ',9900.0,'шт.',2,6,2,15,17,NULL);
INSERT INTO "products" VALUES (25,'L754R4','Полуботинки','Полуботинки kari женские WB2020SS-26, размер 38, цвет: черный',1700.0,'шт.',1,1,1,7,2,NULL);
INSERT INTO "products" VALUES (26,'M542T5','Кроссовки','Кроссовки мужские TOFA',2800.0,'шт.',2,4,2,3,18,NULL);
INSERT INTO "products" VALUES (27,'D268G5','Туфли','Туфли Rieker женские демисезонные, размер 36, цвет коричневый',4399.0,'шт.',1,4,2,12,3,NULL);
INSERT INTO "products" VALUES (28,'T324F5','Сапоги','Сапоги замша Цвет: синий',4699.0,'шт.',1,6,1,5,2,NULL);
INSERT INTO "products" VALUES (29,'K358H6','Тапочки','Тапочки мужские син р.41',599.0,'шт.',2,4,1,2,20,NULL);
INSERT INTO "products" VALUES (30,'H535R5','Ботинки','Женские Ботинки демисезонные',2300.0,'шт.',1,4,2,7,2,NULL);
INSERT INTO "roles" VALUES (1,'Администратор');
INSERT INTO "roles" VALUES (2,'Менеджер');
INSERT INTO "roles" VALUES (3,'Авторизированный клиент');
INSERT INTO "statuses" VALUES (1,'Завершен');
INSERT INTO "statuses" VALUES (2,'Новый');
INSERT INTO "suppliers" VALUES (1,'Kari');
INSERT INTO "suppliers" VALUES (2,'Обувь для вас');
INSERT INTO "users" VALUES (1,1,'Никифорова Весения Николаевна','94d5ous@gmail.com','uzWC67');
INSERT INTO "users" VALUES (2,1,'Сазонов Руслан Германович','uth4iz@mail.com','2L6KZG');
INSERT INTO "users" VALUES (3,1,'Одинцов Серафим Артёмович','yzls62@outlook.com','JlFRCZ');
INSERT INTO "users" VALUES (4,2,'Степанов Михаил Артёмович','1diph5e@tutanota.com','8ntwUp');
INSERT INTO "users" VALUES (5,2,'Ворсин Петр Евгеньевич','tjde7c@yahoo.com','YOyhfR');
INSERT INTO "users" VALUES (6,2,'Старикова Елена Павловна','wpmrc3do@tutanota.com','RSbvHv');
INSERT INTO "users" VALUES (7,3,'Михайлюк Анна Вячеславовна','5d4zbu@tutanota.com','rwVDh9');
INSERT INTO "users" VALUES (8,3,'Ситдикова Елена Анатольевна','ptec8ym@yahoo.com','LdNyos');
INSERT INTO "users" VALUES (9,3,'Ворсин Петр Евгеньевич','1qz4kw@mail.com','gynQMT');
INSERT INTO "users" VALUES (10,3,'Старикова Елена Павловна','4np6se@mail.com','AtnDjr');
COMMIT;
