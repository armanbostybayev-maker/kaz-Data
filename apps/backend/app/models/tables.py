from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from geoalchemy2 import Geometry


class Base(DeclarativeBase):
    pass


class Territory(Base):
    __tablename__ = "territories"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    kato: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    parent_kato: Mapped[str | None] = mapped_column(String(12), index=True)
    name_ru: Mapped[str] = mapped_column(Text)
    name_kk: Mapped[str] = mapped_column(Text)
    admin_level: Mapped[int] = mapped_column(SmallInteger)
    admin_type: Mapped[str] = mapped_column(Text)
    geometry: Mapped[object | None] = mapped_column(Geometry("MULTIPOLYGON", srid=4326))
    centroid: Mapped[object | None] = mapped_column(Geometry("POINT", srid=4326))
    area_km2: Mapped[float | None]
    geometry_source: Mapped[str]
    geometry_valid_at: Mapped[date | None] = mapped_column(Date)
    kato_version: Mapped[str]
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Indicator(Base):
    __tablename__ = "indicators"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True)
    name_ru: Mapped[str]
    name_kk: Mapped[str]
    category: Mapped[str]
    description: Mapped[str | None]
    unit: Mapped[str]
    periodicity: Mapped[str]
    source_url: Mapped[str]
    source_format: Mapped[str]
    aggregation_type: Mapped[str]
    normalization_allowed: Mapped[list[str]] = mapped_column(JSONB)
    formula: Mapped[dict | None] = mapped_column(JSONB)
    territorial_levels: Mapped[list[int]] = mapped_column(ARRAY(SmallInteger))


class IndicatorValue(Base):
    __tablename__ = "indicator_values"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    territory_id: Mapped[int] = mapped_column(ForeignKey("territories.id"), index=True)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id"), index=True)
    period: Mapped[str] = mapped_column(index=True)
    year: Mapped[int] = mapped_column(SmallInteger)
    month: Mapped[int | None] = mapped_column(SmallInteger)
    quarter: Mapped[int | None] = mapped_column(SmallInteger)
    value: Mapped[Decimal | None] = mapped_column(Numeric)
    unit: Mapped[str]
    source_url: Mapped[str]
    source_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    quality_flag: Mapped[str]

