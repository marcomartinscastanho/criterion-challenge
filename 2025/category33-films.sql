INSERT INTO categories_category (id, number, title, year, custom_criteria) VALUES (33, 33, 'Wim Wenders’ Adventures in Moviegoing', 2025, "{}");
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 5 WHERE c.year = 2025 AND c.number = 33;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 524 WHERE c.year = 2025 AND c.number = 33;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 771 WHERE c.year = 2025 AND c.number = 33;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 27960 WHERE c.year = 2025 AND c.number = 33;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 27972 WHERE c.year = 2025 AND c.number = 33;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28093 WHERE c.year = 2025 AND c.number = 33;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28909 WHERE c.year = 2025 AND c.number = 33;
