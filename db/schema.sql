CREATE SCHEMA offers_schema;

CREATE TABLE seller_type (seller_type_id BIGSERIAL NOT NULL PRIMARY KEY,
	seller_type TEXT);

CREATE TABLE seller (seller_id BIGSERIAL NOT NULL PRIMARY KEY,
	source_seller_id TEXT,
	seller_company_name TEXT,
	seller_contact_name TEXT,
	seller_sell_id TEXT,
	seller_email TEXT,
	seller_phone_formatted_numbers TEXT[],
	seller_address_id BIGINT,
	seller_dealer_region TEXT,
	seller_dealer_homepage_url TEXT,
	seller_dealer_review_count INTEGER,
	seller_dealer_rating_average DOUBLE PRECISION,
	seller_dealer_recommend_percentage DOUBLE PRECISION,
	seller_link_car_methods TEXT,
	dealer_contact_person_phone TEXT,
	dealer_contact_person_email TEXT,
	dealer_contact_person_name TEXT,
	dealer_contact_person_position TEXT,
	seller_type_id BIGINT,
	CONSTRAINT seller_type_fk FOREIGN KEY (seller_type_id) REFERENCES seller_type (seller_type_id));

CREATE TABLE make (make_id BIGSERIAL NOT NULL PRIMARY KEY,
	make_name TEXT);

CREATE TABLE model (model_id BIGSERIAL NOT NULL PRIMARY KEY,
	model_name TEXT,
	make_id BIGINT,
	CONSTRAINT model_make_fk FOREIGN KEY (make_id) REFERENCES make (make_id));

CREATE TABLE body_type (body_id BIGSERIAL NOT NULL PRIMARY KEY,
	body TEXT);

CREATE TABLE color (color_id BIGSERIAL NOT NULL PRIMARY KEY,
	color_name TEXT);

CREATE TABLE engine_type (engine_type_id BIGSERIAL NOT NULL PRIMARY KEY,
	engine TEXT);

CREATE TABLE transmission_type (transmission_type_id BIGSERIAL NOT NULL PRIMARY KEY,
	transmission TEXT);

CREATE TABLE publication_type (publication_type_id BIGSERIAL NOT NULL PRIMARY KEY,
	publication TEXT);

CREATE TABLE offer (offer_id BIGSERIAL NOT NULL PRIMARY KEY,
	source_offer_id TEXT,
	make_id BIGINT,
	model_id BIGINT,
	title TEXT,
	engine_capacity INTEGER,
	engine_power_kw INTEGER,
	engine_power_hp INTEGER,
	mileage INTEGER,
	year_of_issue INTEGER,
	vin TEXT,
	original_price NUMERIC,
	tax_deductible BOOLEAN,
	first_registration DATE,
	publication_create_date TIMESTAMP DEFAULT now(),
	publication_update_date TIMESTAMP DEFAULT now(),
	available_now BOOLEAN,
	publication_type TEXT,
	equipment TEXT[],
	image_urls TEXT[],
	description TEXT,
	source_url TEXT,
	city TEXT,
	country TEXT,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
	color_id BIGINT,
	body_type_id BIGINT,
	engine_type_id BIGINT,
	transmission_type_id BIGINT,
	publication_type_id BIGINT,
	seller_id BIGINT,
	CONSTRAINT offer_model_fk FOREIGN KEY (model_id) REFERENCES model (model_id),
	CONSTRAINT offer_make_fk FOREIGN KEY (make_id) REFERENCES make (make_id),
	CONSTRAINT offer_color_fk FOREIGN KEY (color_id) REFERENCES color (color_id),
	CONSTRAINT offer_body_fk FOREIGN KEY (body_type_id) REFERENCES body_type (body_id),
	CONSTRAINT offer_engine_fk FOREIGN KEY (engine_type_id) REFERENCES engine_type (engine_type_id),
	CONSTRAINT offer_transmission_fk FOREIGN KEY (transmission_type_id) REFERENCES transmission_type (transmission_type_id),
	CONSTRAINT offer_publication_fk FOREIGN KEY (publication_type_id) REFERENCES publication_type (publication_type_id),
	CONSTRAINT offer_seller_fk FOREIGN KEY (seller_id) REFERENCES seller (seller_id));