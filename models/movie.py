from bd.database import Base
from sqlalchemy import Column, Integer, String, Float

class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key = True)
    title = Column(String)
    overview = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    category = Column(String)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "overview": self.overview,
            "year": self.year,
            "rating": self.rating,
            "category": self.category
        }


