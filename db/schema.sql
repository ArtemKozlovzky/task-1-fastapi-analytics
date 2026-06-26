SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE public.body_type (
    body_id bigint NOT NULL,
    body text
);

ALTER TABLE public.body_type OWNER TO postgres;

CREATE SEQUENCE public.body_type_body_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.body_type_body_id_seq OWNER TO postgres;

ALTER SEQUENCE public.body_type_body_id_seq OWNED BY public.body_type.body_id;


CREATE TABLE public.color (
    color_id bigint NOT NULL,
    color_name text
);


ALTER TABLE public.color OWNER TO postgres;

CREATE SEQUENCE public.color_color_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.color_color_id_seq OWNER TO postgres;

ALTER SEQUENCE public.color_color_id_seq OWNED BY public.color.color_id;

CREATE TABLE public.engine_type (
    engine_type_id bigint NOT NULL,
    engine text
);


ALTER TABLE public.engine_type OWNER TO postgres;

CREATE SEQUENCE public.engine_type_engine_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.engine_type_engine_type_id_seq OWNER TO postgres;

ALTER SEQUENCE public.engine_type_engine_type_id_seq OWNED BY public.engine_type.engine_type_id;

CREATE TABLE public.export_jobs (
    job_id uuid DEFAULT gen_random_uuid() NOT NULL,
    status character varying DEFAULT 'pending'::character varying NOT NULL,
    filters jsonb NOT NULL,
    file_path text,
    created_at timestamp without time zone DEFAULT now()
);

ALTER TABLE public.export_jobs OWNER TO postgres;

CREATE TABLE public.make (
    make_id bigint NOT NULL,
    make_name text
);

ALTER TABLE public.make OWNER TO postgres;

CREATE SEQUENCE public.make_make_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.make_make_id_seq OWNER TO postgres;

ALTER SEQUENCE public.make_make_id_seq OWNED BY public.make.make_id;

CREATE TABLE public.model (
    model_id bigint NOT NULL,
    model_name text,
    make_id bigint
);

ALTER TABLE public.model OWNER TO postgres;

CREATE SEQUENCE public.model_model_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.model_model_id_seq OWNER TO postgres;

ALTER SEQUENCE public.model_model_id_seq OWNED BY public.model.model_id;

CREATE TABLE public.offer (
    offer_id bigint NOT NULL,
    source_offer_id text,
    make_id bigint,
    model_id bigint,
    title text,
    engine_capacity integer,
    engine_power_kw integer,
    engine_power_hp integer,
    mileage integer,
    year_of_issue integer,
    vin text,
    original_price numeric,
    tax_deductible boolean,
    first_registration date,
    publication_create_date timestamp without time zone DEFAULT now(),
    publication_update_date timestamp without time zone DEFAULT now(),
    available_now boolean,
    equipment text[],
    image_urls text[],
    description text,
    source_url text,
    city text,
    country text,
    created_at timestamp with time zone DEFAULT now(),
    color_id bigint,
    body_type_id bigint,
    engine_type_id bigint,
    transmission_type_id bigint,
    publication_type_id bigint,
    seller_id bigint
);

ALTER TABLE public.offer OWNER TO postgres;

CREATE SEQUENCE public.offer_offer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.offer_offer_id_seq OWNER TO postgres;

ALTER SEQUENCE public.offer_offer_id_seq OWNED BY public.offer.offer_id;

CREATE TABLE public.publication_type (
    publication_type_id bigint NOT NULL,
    publication text
);

ALTER TABLE public.publication_type OWNER TO postgres;

CREATE SEQUENCE public.publication_type_publication_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.publication_type_publication_type_id_seq OWNER TO postgres;

ALTER SEQUENCE public.publication_type_publication_type_id_seq OWNED BY public.publication_type.publication_type_id;

CREATE TABLE public.seller (
    seller_id bigint NOT NULL,
    source_seller_id text,
    seller_company_name text,
    seller_contact_name text,
    seller_sell_id text,
    seller_email text,
    seller_phone_formatted_numbers text[],
    seller_address_id bigint,
    seller_dealer_region text,
    seller_dealer_homepage_url text,
    seller_dealer_review_count integer,
    seller_dealer_rating_average double precision,
    seller_dealer_recommend_percentage double precision,
    seller_link_car_methods text,
    dealer_contact_person_phone text,
    dealer_contact_person_email text,
    dealer_contact_person_name text,
    dealer_contact_person_position text,
    seller_type_id bigint
);

ALTER TABLE public.seller OWNER TO postgres;

CREATE SEQUENCE public.seller_seller_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.seller_seller_id_seq OWNER TO postgres;

ALTER SEQUENCE public.seller_seller_id_seq OWNED BY public.seller.seller_id;

CREATE TABLE public.seller_type (
    seller_type_id bigint NOT NULL,
    seller text
);

ALTER TABLE public.seller_type OWNER TO postgres;

CREATE SEQUENCE public.seller_type_seller_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.seller_type_seller_type_id_seq OWNER TO postgres;

ALTER SEQUENCE public.seller_type_seller_type_id_seq OWNED BY public.seller_type.seller_type_id;

CREATE TABLE public.transmission_type (
    transmission_type_id bigint NOT NULL,
    transmission text
);

ALTER TABLE public.transmission_type OWNER TO postgres;

CREATE SEQUENCE public.transmission_type_transmission_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.transmission_type_transmission_type_id_seq OWNER TO postgres;

ALTER SEQUENCE public.transmission_type_transmission_type_id_seq OWNED BY public.transmission_type.transmission_type_id;

ALTER TABLE ONLY public.body_type ALTER COLUMN body_id SET DEFAULT nextval('public.body_type_body_id_seq'::regclass);

ALTER TABLE ONLY public.color ALTER COLUMN color_id SET DEFAULT nextval('public.color_color_id_seq'::regclass);

ALTER TABLE ONLY public.engine_type ALTER COLUMN engine_type_id SET DEFAULT nextval('public.engine_type_engine_type_id_seq'::regclass);

ALTER TABLE ONLY public.make ALTER COLUMN make_id SET DEFAULT nextval('public.make_make_id_seq'::regclass);

ALTER TABLE ONLY public.model ALTER COLUMN model_id SET DEFAULT nextval('public.model_model_id_seq'::regclass);

ALTER TABLE ONLY public.offer ALTER COLUMN offer_id SET DEFAULT nextval('public.offer_offer_id_seq'::regclass);

ALTER TABLE ONLY public.publication_type ALTER COLUMN publication_type_id SET DEFAULT nextval('public.publication_type_publication_type_id_seq'::regclass);

ALTER TABLE ONLY public.seller ALTER COLUMN seller_id SET DEFAULT nextval('public.seller_seller_id_seq'::regclass);

ALTER TABLE ONLY public.seller_type ALTER COLUMN seller_type_id SET DEFAULT nextval('public.seller_type_seller_type_id_seq'::regclass);

ALTER TABLE ONLY public.transmission_type ALTER COLUMN transmission_type_id SET DEFAULT nextval('public.transmission_type_transmission_type_id_seq'::regclass);

ALTER TABLE ONLY public.body_type
    ADD CONSTRAINT body_type_pkey PRIMARY KEY (body_id);

ALTER TABLE ONLY public.color
    ADD CONSTRAINT color_pkey PRIMARY KEY (color_id);

ALTER TABLE ONLY public.engine_type
    ADD CONSTRAINT engine_type_pkey PRIMARY KEY (engine_type_id);

ALTER TABLE ONLY public.export_jobs
    ADD CONSTRAINT export_jobs_pkey PRIMARY KEY (job_id);

ALTER TABLE ONLY public.make
    ADD CONSTRAINT make_pkey PRIMARY KEY (make_id);

ALTER TABLE ONLY public.model
    ADD CONSTRAINT model_pkey PRIMARY KEY (model_id);

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_pkey PRIMARY KEY (offer_id);

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_source_offer_id_key UNIQUE (source_offer_id);

ALTER TABLE ONLY public.publication_type
    ADD CONSTRAINT publication_type_pkey PRIMARY KEY (publication_type_id);

ALTER TABLE ONLY public.seller
    ADD CONSTRAINT seller_pkey PRIMARY KEY (seller_id);

ALTER TABLE ONLY public.seller_type
    ADD CONSTRAINT seller_type_pkey PRIMARY KEY (seller_type_id);

ALTER TABLE ONLY public.transmission_type
    ADD CONSTRAINT transmission_type_pkey PRIMARY KEY (transmission_type_id);

ALTER TABLE ONLY public.model
    ADD CONSTRAINT model_make_fk FOREIGN KEY (make_id) REFERENCES public.make(make_id);

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_body_fk FOREIGN KEY (body_type_id) REFERENCES public.body_type(body_id);

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_color_fk FOREIGN KEY (color_id) REFERENCES public.color(color_id);

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_engine_fk FOREIGN KEY (engine_type_id) REFERENCES public.engine_type(engine_type_id);

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_make_fk FOREIGN KEY (make_id) REFERENCES public.make(make_id);

ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_model_fk FOREIGN KEY (model_id) REFERENCES public.model(model_id);


ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_publication_fk FOREIGN KEY (publication_type_id) REFERENCES public.publication_type(publication_type_id);


ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_seller_fk FOREIGN KEY (seller_id) REFERENCES public.seller(seller_id);


ALTER TABLE ONLY public.offer
    ADD CONSTRAINT offer_transmission_fk FOREIGN KEY (transmission_type_id) REFERENCES public.transmission_type(transmission_type_id);


ALTER TABLE ONLY public.seller
    ADD CONSTRAINT seller_type_fk FOREIGN KEY (seller_type_id) REFERENCES public.seller_type(seller_type_id);
