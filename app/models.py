from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Model(DeclarativeBase):
    pass

class OfferOrm(Model):
    __tablename__ = "offer"

    offer_id: Mapped[int] = mapped_column(primary_key=True)
    source_offer_id: Mapped[str | None]
    make_id: Mapped[int] = mapped_column(ForeignKey('make.make_id'))
    model_id: Mapped[int] = mapped_column(ForeignKey('model.model_id'))
    title: Mapped[str]
    engine_capacity: Mapped[int | None]
    engine_power_kw: Mapped[int | None]
    engine_power_hp: Mapped[int | None]
    mileage: Mapped[int | None]
    year_of_issue: Mapped[str | None]
    vin: Mapped[str | None]
    original_price: Mapped[int | None]
    tax_deductible: Mapped[bool | None]
    first_registration: Mapped [str | None]
    publication_create_date: Mapped [str | None]
    publication_update_date: Mapped [str | None]
    available_now: Mapped [bool | None]
    equipment: Mapped[str | None]
    image_urls: Mapped[str | None]
    description: Mapped[str | None]
    source_url: Mapped[str | None]
    city: Mapped[str | None]
    country: Mapped[str | None]
    created_at: Mapped[str | None]
    color_id: Mapped[int] = mapped_column(ForeignKey('color.color_id'))
    body_type_id: Mapped[int] = mapped_column(ForeignKey('body_type.body_id'))
    engine_type_id: Mapped[int] = mapped_column(ForeignKey('engine_type.engine_type_id'))
    transmission_type_id: Mapped[int] = mapped_column(ForeignKey('transmission_type.transmission_type_id'))
    publication_type_id: Mapped[int] = mapped_column(ForeignKey('publication_type.publication_type_id'))
    seller_id: Mapped[int | None] = mapped_column(ForeignKey('seller.seller_id'))

    make = relationship('MakeOrm', back_populates='offers')
    model = relationship('ModelOrm', back_populates='offers')
    seller = relationship('SellerOrm', back_populates='offers')
    color = relationship('ColorOrm', back_populates='offers')
    body_type = relationship('BodyTypeOrm', back_populates='offers')
    engine_type = relationship('EngineTypeOrm', back_populates='offers')
    transmission_type = relationship('TransmissionTypeOrm', back_populates='offers')
    publication_type = relationship('PublicationTypeOrm', back_populates='offers')


class SellerOrm(Model):
    __tablename__ = "seller"

    seller_id: Mapped[int] = mapped_column(primary_key=True)
    source_seller_id: Mapped[str | None]
    seller_company_name: Mapped[str | None]
    seller_contact_name: Mapped[str | None]
    seller_sell_id: Mapped[str | None]
    seller_email: Mapped[str | None]
    seller_phone_formatted_numbers: Mapped[str | None]
    seller_address_id: Mapped[str | None]
    seller_dealer_region: Mapped[str | None]
    seller_dealer_homepage_url: Mapped[str | None]
    seller_dealer_review_count: Mapped[int | None]
    seller_dealer_ration_average: Mapped[float | None]
    seller_dealer_recommend_percentage: Mapped[float | None]
    seller_link_car_methods: Mapped[str | None]
    dealer_contact_person_phone: Mapped[str | None]
    dealer_contact_person_email: Mapped[str | None]
    dealer_contact_person_name: Mapped[str | None]
    dealer_contact_person_position: Mapped[str | None]
    seller_type_id: Mapped[int | None] = mapped_column(ForeignKey('seller_type.seller_type_id'))

    offers = relationship("OfferOrm", back_populates='seller')
    seller_type = relationship('SellerTypeOrm', back_populates='sellers')

class BodyTypeOrm(Model):
    __tablename__ = "body_type"

    body_id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str]

    offers = relationship("OfferOrm", back_populates='body_type')

class ColorOrm(Model):
    __tablename__ = "color"

    color_id: Mapped[int] = mapped_column(primary_key=True)
    color_name: Mapped[str]

    offers = relationship("OfferOrm", back_populates='color')

class EngineTypeOrm(Model):
    __tablename__ = "engine_type"

    engine_type_id: Mapped[int] = mapped_column(primary_key=True)
    engine: Mapped[str]

    offers = relationship("OfferOrm", back_populates='engine_type')

class MakeOrm(Model):
    __tablename__ = "make"

    make_id: Mapped[int] = mapped_column(primary_key=True)
    make_name: Mapped[str]

    offers = relationship("OfferOrm", back_populates='make')
    models = relationship('ModelOrm', back_populates='make')

class ModelOrm(Model):
    __tablename__ = "model"

    model_id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str]
    make_id: Mapped[int] = mapped_column(ForeignKey('make.make_id'))

    offers = relationship("OfferOrm", back_populates='model')
    make = relationship('MakeOrm', back_populates='models')

class PublicationTypeOrm(Model):
    __tablename__ = "publication_type"

    publication_type_id: Mapped[int] = mapped_column(primary_key=True)
    publication: Mapped[str]

    offers = relationship("OfferOrm", back_populates='publication_type')

class SellerTypeOrm(Model):
    __tablename__ = "seller_type"

    seller_type_id: Mapped[int] = mapped_column(primary_key=True)
    seller: Mapped[str]

    sellers = relationship("SellerOrm", back_populates='seller_type')

class TransmissionTypeOrm(Model):
    __tablename__ = "transmission_type"

    transmission_type_id: Mapped[int] = mapped_column(primary_key=True)
    transmission: Mapped[str | None]

    offers = relationship("OfferOrm", back_populates='transmission_type')