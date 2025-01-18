INSERT INTO categories_category (id, number, title, year, custom_criteria) VALUES (48, 48, 'Australian film', 2025, "{}");
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 565 WHERE c.year = 2025 AND c.number = 48;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 685 WHERE c.year = 2025 AND c.number = 48;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 742 WHERE c.year = 2025 AND c.number = 48;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 749 WHERE c.year = 2025 AND c.number = 48;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 27766 WHERE c.year = 2025 AND c.number = 48;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 29065 WHERE c.year = 2025 AND c.number = 48;
INSERT INTO categories_category_films (category_id, film_id) SELECT c.id, f.cc_id FROM categories_category c JOIN films_film f ON f.cc_id = 30424 WHERE c.year = 2025 AND c.number = 48;
