INSERT INTO categories_category (id, number, title, year, custom_criteria) VALUES (18, 18, 'William Friedkin’s Closet Picks', 2025, "{}");
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 150 WHERE c.year = 2025 AND c.number = 18;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 371 WHERE c.year = 2025 AND c.number = 18;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 558 WHERE c.year = 2025 AND c.number = 18;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 622 WHERE c.year = 2025 AND c.number = 18;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 820 WHERE c.year = 2025 AND c.number = 18;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 27751 WHERE c.year = 2025 AND c.number = 18;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 28025 WHERE c.year = 2025 AND c.number = 18;
