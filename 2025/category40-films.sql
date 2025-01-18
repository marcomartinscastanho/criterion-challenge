INSERT INTO categories_category (id, number, title, year, custom_criteria) VALUES (40, 40, 'Isabella Rossellini’s Adventures in Moviegoing', 2025, "{}");
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 7 WHERE c.year = 2025 AND c.number = 40;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 8 WHERE c.year = 2025 AND c.number = 40;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 185 WHERE c.year = 2025 AND c.number = 40;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 544 WHERE c.year = 2025 AND c.number = 40;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 27563 WHERE c.year = 2025 AND c.number = 40;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28454 WHERE c.year = 2025 AND c.number = 40;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 30569 WHERE c.year = 2025 AND c.number = 40;
