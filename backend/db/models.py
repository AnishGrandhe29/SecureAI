"""
ORM models mirroring the 6 CSV schemas exactly.
All primary keys as Integer, dates as Date, floats as Float.
"""

from sqlalchemy import Column, Integer, String, Float, Date
from db.database import Base


class Movie(Base):
    __tablename__ = "movies"

    movie_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False, index=True)
    release_year = Column(Integer, nullable=False, index=True)
    director = Column(String, nullable=False)
    runtime_min = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    budget_usd = Column(Float, nullable=False)
    revenue_usd = Column(Float, nullable=False)


class Viewer(Base):
    __tablename__ = "viewers"

    viewer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age_group = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    subscription_tier = Column(String, nullable=False)
    joined_date = Column(Date, nullable=False)


class WatchActivity(Base):
    __tablename__ = "watch_activity"

    activity_id = Column(Integer, primary_key=True, index=True)
    viewer_id = Column(Integer, nullable=False, index=True)
    movie_id = Column(Integer, nullable=False, index=True)
    watch_date = Column(Date, nullable=False)
    watch_duration_min = Column(Integer, nullable=False)
    completion_pct = Column(Float, nullable=False)
    device = Column(String, nullable=False)


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    viewer_id = Column(Integer, nullable=False, index=True)
    movie_id = Column(Integer, nullable=False, index=True)
    rating = Column(Float, nullable=False)
    sentiment = Column(String, nullable=False)
    review_date = Column(Date, nullable=False)
    review_text = Column(String, nullable=False)


class MarketingSpend(Base):
    __tablename__ = "marketing_spend"

    campaign_id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, nullable=False, index=True)
    channel = Column(String, nullable=False)
    spend_usd = Column(Float, nullable=False)
    impressions = Column(Integer, nullable=False)
    clicks = Column(Integer, nullable=False)
    conversions = Column(Integer, nullable=False)
    campaign_month = Column(String, nullable=False)


class RegionalPerformance(Base):
    __tablename__ = "regional_performance"

    region_id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    movie_id = Column(Integer, nullable=False, index=True)
    views = Column(Integer, nullable=False)
    engagement_score = Column(Float, nullable=False)
    revenue_usd = Column(Float, nullable=False)
    month = Column(String, nullable=False)
