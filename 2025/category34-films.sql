INSERT INTO categories_category (id, number, title, year, custom_criteria) VALUES (34, 34, 'South American film', 2025, "{}");
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28113 WHERE c.year = 2025 AND c.number = 34;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28407 WHERE c.year = 2025 AND c.number = 34;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 30307 WHERE c.year = 2025 AND c.number = 34;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 30308 WHERE c.year = 2025 AND c.number = 34;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 33537 WHERE c.year = 2025 AND c.number = 34;
