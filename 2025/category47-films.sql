INSERT INTO categories_category (id, number, title, year, custom_criteria) VALUES (47, 47, 'Rachel Kushner’s Adventures in Moviegoing', 2025, "{}");
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 9 WHERE c.year = 2025 AND c.number = 47;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 10 WHERE c.year = 2025 AND c.number = 47;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 304 WHERE c.year = 2025 AND c.number = 47;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 755 WHERE c.year = 2025 AND c.number = 47;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 2337 WHERE c.year = 2025 AND c.number = 47;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28112 WHERE c.year = 2025 AND c.number = 47;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28660 WHERE c.year = 2025 AND c.number = 47;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 29450 WHERE c.year = 2025 AND c.number = 47;
