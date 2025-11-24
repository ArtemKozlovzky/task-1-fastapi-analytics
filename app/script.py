import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

source_conn = psycopg2.connect(
    host=os.getenv("source_host"),
    dbname=os.getenv("source_dbname"),
    user=os.getenv("source_user"),
    password=os.getenv("source_password"),
    sslmode="require"
)

target_conn = psycopg2.connect(
    host=os.getenv("target_host"),
    dbname=os.getenv("target_dbname"),
    user=os.getenv("target_user"),
    password=os.getenv("target_password")
)

source_cur = source_conn.cursor()
target_cur = target_conn.cursor()

try:
    source_cur.execute("""SELECT DISTINCT make, model, color, body_type, engine_type,
                          publication_type, seller_type, transmission_type  FROM source.offers;""")
    unique_values = source_cur.fetchall()

    make_map = {}
    for make_name in set(row[0] for row in unique_values):
        target_cur.execute("SELECT make_id FROM make WHERE make_name=%s;", (make_name,))
        result = target_cur.fetchone()
        if result:
            make_map[make_name] = result[0]
        else:
            target_cur.execute(
                "INSERT INTO make (make_name) VALUES (%s) RETURNING make_id;",
                (make_name,)
            )
            make_map[make_name] = target_cur.fetchone()[0]

    model_map = {}
    for model_name, make_name in set((row[1], row[0]) for row in unique_values):
        target_cur.execute(
            "SELECT model_id FROM model WHERE model_name=%s AND make_id=%s;",
            (model_name, make_map[make_name])
        )
        result = target_cur.fetchone()
        if result:
            model_map[(model_name, make_name)] = result[0]
        else:
            target_cur.execute(
                "INSERT INTO model (model_name, make_id) VALUES (%s, %s) RETURNING model_id;",
                (model_name, make_map[make_name])
            )
            model_map[(model_name, make_name)] = target_cur.fetchone()[0]

    color_map = {}
    for color_name in set(row[2] for row in unique_values):
        target_cur.execute("SELECT color_id FROM color WHERE color_name=%s;", (color_name,))
        result = target_cur.fetchone()
        if result:
            color_map[color_name] = result[0]
        else:
            target_cur.execute(
                "INSERT INTO color (color_name) VALUES (%s) RETURNING color_id;",
                (color_name,)
            )
            color_map[color_name] = target_cur.fetchone()[0]

    body_type_map = {}
    for body in set(row[3] for row in unique_values):
        target_cur.execute("SELECT body_id FROM body_type WHERE body=%s;", (body,))
        result = target_cur.fetchone()
        if result:
            body_type_map[body] = result[0]
        else:
            target_cur.execute(
                "INSERT INTO body_type (body) VALUES (%s) RETURNING body_id;",
                (body,)
            )
            body_type_map[body] = target_cur.fetchone()[0]

    engine_type_map = {}
    for engine in set(row[4] for row in unique_values):
        target_cur.execute("SELECT engine_type_id FROM engine_type WHERE engine=%s;", (engine,))
        result = target_cur.fetchone()
        if result:
            engine_type_map[engine] = result[0]
        else:
            target_cur.execute(
                "INSERT INTO engine_type (engine) VALUES (%s) RETURNING engine_type_id;",
                (engine,)
            )
            engine_type_map[engine] = target_cur.fetchone()[0]

    publication_type_map = {}
    for publication in set(row[5] for row in unique_values):
        target_cur.execute("SELECT publication_type_id FROM publication_type WHERE publication=%s;", (publication,))
        result = target_cur.fetchone()
        if result:
            publication_type_map[publication] = result[0]
        else:
            target_cur.execute(
                "INSERT INTO publication_type (publication) VALUES (%s) RETURNING publication_type_id;",
                (publication,)
            )
            publication_type_map[publication] = target_cur.fetchone()[0]

    seller_type_map = {}
    for seller in set(row[6] for row in unique_values):
        target_cur.execute("SELECT seller_type_id FROM seller_type WHERE seller=%s;",
                            (seller,))
        result = target_cur.fetchone()
        if result:
            seller_type_map[seller] = result[0]
        else:
            target_cur.execute(
                "INSERT INTO seller_type (seller) VALUES (%s) RETURNING seller_type_id;",
                (seller,)
            )
            seller_type_map[seller] = target_cur.fetchone()[0]

    transmission_type_map = {}
    for transmission in set(row[7] for row in unique_values):
        target_cur.execute("SELECT transmission_type_id FROM transmission_type WHERE transmission=%s;",
                            (transmission,))
        result = target_cur.fetchone()
        if result:
            transmission_type_map[transmission] = result[0]
        else:
            target_cur.execute(
                "INSERT INTO transmission_type (transmission) VALUES (%s) RETURNING transmission_type_id;",
                (transmission,)
            )
            transmission_type_map[transmission] = target_cur.fetchone()[0]

    source_cur.execute("SELECT * FROM source.offers;")
    offers = source_cur.fetchall()

    for (source_offer_id, source_make, source_model, source_title, source_color, source_body_type, source_engine_type, source_engine_capacity, source_engine_power_kw,
                    source_engine_power_hp, source_mileage, source_transmission_type, source_year_of_issue, source_vin, source_original_price, source_tax_deductible, source_first_registration,
                    source_publication_create_date, source_publication_update_date, source_available_now, source_publication_type, source_equipment, source_image_urls, source_description,
                    s_source_urls, source_city, source_country, source_seller_id, source_seller_company_name, source_seller_contact_name, source_seller_sell_id, source_seller_type,
                    source_seller_email, source_seller_phone_formatted_numbers, source_seller_address_id, source_seller_dealer_region, source_seller_dealer_homepage_url,
                    source_seller_dealer_review_count, source_seller_dealer_rating_average, source_seller_dealer_recommend_percentage, source_seller_link_car_methods,
                    source_dealer_contact_person_phone, source_dealer_contact_person_email, source_dealer_contact_person_name, source_dealer_contact_person_position, source_created_at) in offers:
        make_id = make_map[source_make]
        model_id = model_map[(source_model, source_make)]
        color_id = color_map[source_color]
        body_type_id = body_type_map[source_body_type]
        engine_type_id = engine_type_map[source_engine_type]
        publication_type_id = publication_type_map[source_publication_type]
        seller_type_id = seller_type_map[source_seller_type]
        transmission_type_id = transmission_type_map[source_transmission_type]

        target_cur.execute("""
                INSERT INTO seller (source_seller_id, seller_company_name, seller_contact_name, seller_sell_id, seller_email, seller_phone_formatted_numbers, 
                seller_address_id, seller_dealer_region, seller_dealer_homepage_url, seller_dealer_review_count, seller_dealer_rating_average, 
                seller_dealer_recommend_percentage, seller_link_car_methods, dealer_contact_person_phone, dealer_contact_person_email, dealer_contact_person_name, 
                dealer_contact_person_position, seller_type_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (source_seller_id, source_seller_company_name, source_seller_contact_name, source_seller_sell_id,source_seller_email,
                  source_seller_phone_formatted_numbers, source_seller_address_id, source_seller_dealer_region,source_seller_dealer_homepage_url,
                  source_seller_dealer_review_count, source_seller_dealer_rating_average, source_seller_dealer_recommend_percentage, source_seller_link_car_methods,
                  source_dealer_contact_person_phone, source_dealer_contact_person_email, source_dealer_contact_person_name, source_dealer_contact_person_position, seller_type_id))

        target_cur.execute("""
                SELECT seller_id FROM seller
                ORDER BY seller_id DESC
                LIMIT 1
            """,)
        seller_id = target_cur.fetchone()

        target_cur.execute("""
            INSERT INTO offer (source_offer_id, make_id, model_id, title, engine_capacity, engine_power_kw, engine_power_hp, mileage, year_of_issue, 
            vin, original_price, tax_deductible, first_registration, publication_create_date, publication_update_date, available_now, equipment, image_urls, 
            description, source_url, city, country, created_at, color_id, body_type_id, engine_type_id, transmission_type_id, publication_type_id, seller_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (source_offer_id, make_id, model_id, source_title, source_engine_capacity, source_engine_power_kw, source_engine_power_hp, source_mileage,
              source_year_of_issue, source_vin, source_original_price, source_tax_deductible, source_first_registration, source_publication_create_date,
              source_publication_update_date, source_available_now, source_equipment, source_image_urls, source_description, s_source_urls, source_city,
              source_country, source_created_at, color_id, body_type_id, engine_type_id, transmission_type_id, publication_type_id, seller_id))

    target_conn.commit()

except Exception as e:
    print(f"Error: {e}")
    target_conn.rollback()
finally:
    target_cur.close()
    source_cur.close()
    target_conn.close()
    source_conn.close()