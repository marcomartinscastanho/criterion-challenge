INSERT INTO categories_category (id, number, title, year, custom_criteria) VALUES (3, 3, 'Directed by Robert Altman', 2025, NULL);
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 376 WHERE c.year = 2025 AND c.number = 3;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 712 WHERE c.year = 2025 AND c.number = 3;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 952 WHERE c.year = 2025 AND c.number = 3;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 955 WHERE c.year = 2025 AND c.number = 3;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28427 WHERE c.year = 2025 AND c.number = 3;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28712 WHERE c.year = 2025 AND c.number = 3;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28835 WHERE c.year = 2025 AND c.number = 3;
