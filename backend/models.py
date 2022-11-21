from typing import Mapping, Union

from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

import model_types


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
    def get_meals(cls):
        return [{
            'calories': meal.calories,
            'created_at': meal.created_at,
            'id': meal.id,
            'meal_type': meal.meal_type,
            'protein': meal.protein
        } for meal in cls.query.all()]

    @classmethod
    def find_meal(cls, user_id: int, meal_id: int) -> 'Meal':
        return cls.query.join(User).filter(
            User.id == user_id
        ).filter(cls.id == meal_id).first()
    
    def update(self, data: Mapping[str, Union[str, int]]) -> bool:
        try:
            for key in data:
                if key != 'id':
                    setattr(self, key, data[key])
            db.session.commit()
            return True
        except Exception:
            return False

    def delete(self) -> bool:
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception:
            return False


class User(db.Model):
    # __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    meals = relationship("Meal", order_by=Meal.id, back_populates="user")

    @classmethod
    def save_meal(cls, user_id: int, data: Mapping[str, Union[str, int]]):
        try:
            current_user = cls.find_user(user_id)
            current_user.meals.append(Meal(**data['meal']))
            db.session.add(current_user)
            db.session.commit()
            return True
        except Exception:
            return False

    @classmethod
    def update_meal(cls, user_id: int, data: Mapping[str, Union[str, int]]):
        try:
            meal_data = data['meal']
            current_meal = cls.find_meal(user_id, meal_data['id'])
            return current_meal.update(meal_data)
        except Exception as e:
            print('Error: ', e)
            return False

    @classmethod
    def find_user(cls, user_id: int) -> 'User':
        return cls.query.filter(cls.id == user_id).first()

    @classmethod
    def get_meals(cls, user_id: int) -> dict:
        return [{
            'calories': meal.calories,
            'created_at': meal.created_at,
            'id': meal.id,
            'meal_type': meal.meal_type,
            'protein': meal.protein
        } for meal in cls.find_user(user_id).meals]
    
    @classmethod
    def find_meal(cls, user_id, meal_id: int) -> 'Meal':
        return Meal.find_meal(user_id, meal_id)
    
    @classmethod
    def delete_meal(cls, user_id, data: Mapping[str, Union[str, int]]) -> bool:
        try:
            meal_data = data['meal']
            current_meal = cls.find_meal(user_id, meal_data['id'])
            current_meal.delete()
            return True
        except Exception:
            return False
