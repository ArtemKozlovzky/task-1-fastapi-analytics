CREATE TABLE cars
(
	car_id BIGINT NOT NULL PRIMARY KEY,
    make TEXT,
    model TEXT,
    color TEXT,
    body_type TEXT,
    engine_type TEXT,
    engine_capacity INTEGER,
    engine_power_kw INTEGER,
    engine_power_hp INTEGER,
    mileage INTEGER,
    transmission_type TEXT,
    year_of_issue INTEGER,
    vin TEXT,
    first_registration DATE,
    equipment TEXT[],
    image_urls TEXT[],
);

CREATE TABLE offers
(
    offer_id BIGINT NOT NULL PRIMARY KEY,
    title TEXT,
    original_price NUMERIC,
    tax_deductible BOOLEAN,
    publication_create_date TIMESTAMP DEFAULT now(),
    publication_update_date TIMESTAMP DEFAULT now(),
    available_now BOOLEAN,
    publication_type TEXT,
    description TEXT,
    source_url TEXT,
    city TEXT,
    country TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    seller_id BIGINT,
    car_id BIGINT,
    CONSTRAINT (offers_car_id_fk) FOREIGN KEY (car_id) REFERENCES cars (car_id),
);

CREATE TABLE sells
(
	sell_id BIGINT NOT NULL PRIMARY KEY,
	car_id BIGINT,
	offer_id BIGINT,
	CONSTRAINT (sells_car_id_fk) FOREIGN KEY (car_id) REFERENCES cars(car_id),
	CONSTRAINT (sells_offer_id_fk) FOREIGN KEY (offer_id) REFERENCES offers(offer_id)
);

CREATE TABLE sellers
(
	seller_id BIGINT NOT NULL PRIMARY KEY,
	seller_company_name TEXT,
	seller_contact_name TEXT,
	seller_type TEXT,
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
	seller_sell_id TEXT,
	CONSTRAINT (sellers_sell_id_fk) FOREIGN KEY (seller_sell_id) REFERENCES sells (sell_id)
);

ALTER TABLE offers
ADD CONSTRAINT (offers_seller_id_fk) FOREIGN KEY (seller_id) REFERENCES sellers (seller_id);