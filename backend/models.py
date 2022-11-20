from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Meal(db.Model):
    __tablename__ = "meals"
    id = db.Column(db.Integer, primary_key=True)
    meal_type = db.Column(db.Text, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="meals")
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    @classmethod
    def create_fake_meal(cls):
        meal = cls(meal_type='Food',
                   calories=100,
                   protein=100,
                   user_id=1)
        print('Meal: ', meal)
        db.session.add(meal)
        db.session.commit()
        return meal


class User(db.Model):
    # __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    meals = relationship("Meal", order_by=Meal.id, back_populates="user")

    @classmethod
    def find_user(cls, user_id: int) -> 'User':
        return cls.query.filter(cls.id == user_id).first()

    @classmethod
    def get_meals(cls, user_id: int):
        return [{
            'calories': meal.calories,
            'created_at': meal.created_at,
            'id': meal.id,
            'meal_type': meal.meal_type,
            'protein': meal.protein
        } for meal in cls.find_user(user_id).meals]

    @classmethod
    def create_fake_user(cls):
        user = cls(username='Bob')
        print('User: ', user)
        db.session.add(user)
        db.session.commit()
        return user


# class Photo(db.Model):
#     created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
#     id = db.Column(db.Integer, primary_key=True)
#     image_url = db.Column(db.Text, nullable=False)

#     @classmethod
#     def get_photos(cls):
#         return [{
#             'created_at': photo.created_at.strftime('%c'),
#             'image_url': photo.image_url
#         } for photo in cls.query.all()]


#     @classmethod
#     def save_photo(cls, image_url):
#         photo = cls(image_url=image_url)
#         db.session.add(photo)
#         db.session.commit()


#     @classmethod
#     def __delete_photos(cls):
#         for photo in cls.query.all():
#             db.session.delete(photo)
#             db.session.commit()


def delete_all():
    Meal.__table__.drop(db.engine)
    User.__table__.drop(db.engine)
