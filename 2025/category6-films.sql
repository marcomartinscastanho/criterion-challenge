INSERT INTO films_film (cc_id, title, spine, year, country, letterboxd) VALUES (1, 'Rocco and His Brothers', NULL, 1960, 'IT', 'https://boxd.it/20bG');
INSERT INTO categories_category (id, number, title, year, custom_criteria) VALUES (6, 6, 'John Turturro’s Adventures in Moviegoing', 2025, {});
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 1 WHERE c.year = 2025 AND c.number = 6;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 165 WHERE c.year = 2025 AND c.number = 6;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 175 WHERE c.year = 2025 AND c.number = 6;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 820 WHERE c.year = 2025 AND c.number = 6;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 877 WHERE c.year = 2025 AND c.number = 6;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 27899 WHERE c.year = 2025 AND c.number = 6;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 30717 WHERE c.year = 2025 AND c.number = 6;
