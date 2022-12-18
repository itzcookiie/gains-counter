import collections
from functools import reduce
import enum
import datetime
from typing import Iterator, Mapping, Union

from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


DATETIME_FILTER = "%Y-%m-%d %H:%M%S"

def calculate_goal_totals_wrapper(results):
    def calculate_goal_totals(total, current_created_at_dates):
        min_created_at, max_created_at = current_created_at_dates
        meals_eaten_on_day = results.filter(
            (Meal.created_at >= min_created_at),
            (Meal.created_at < max_created_at)
        )
        result = {
            'created_at': min_created_at.timestamp(),
            'total_calories': sum(meal.calories for meal in meals_eaten_on_day),
            'total_protein': sum(meal.protein for meal in meals_eaten_on_day),
            'meals': [meal.serialise_meal() for meal in meals_eaten_on_day]
        }
        return [*total, result]

    return calculate_goal_totals


def get_unique_dates(all_unique_dates, cur_date):
    print(cur_date.strftime(DATETIME_FILTER))
    return ([*all_unique_dates, cur_date]
     if cur_date.strftime(DATETIME_FILTER) not in all_unique_dates
    else [*all_unique_dates])


def get_date_in_datetime_form(date_arg: datetime.datetime) -> str:
    return datetime.datetime.strptime(date_arg, DATETIME_FILTER)


def get_start_of_day(datetime_arg: datetime.datetime) -> datetime.datetime:
    return datetime.datetime.combine(datetime_arg, datetime.datetime.min.time())

db = SQLAlchemy()


class ResultMessage(enum.Enum):
    USER_ALREADY_EXISTS = 'User already exists!'
    LOGIN_FAILED = 'Unexpected exception raised. Could not login or sign up'
    LOGIN_SUCCESS = 'Login success!'


class Meal(db.Model):
    __tablename__ = "meals"
    id = db.Column(db.Integer, primary_key=True)
    meal_type = db.Column(db.Text, nullable=False)
    meal_name = db.Column(db.Text, nullable=False)
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
            'meal_name': meal.meal_name,
            'protein': meal.protein
        } for meal in cls.query.all()]

    @classmethod
    def get_results_for_everyday(cls, user_id: int) -> dict:
        query = cls.query.join(User)
        user_meals = query.filter(User.id == user_id)
        unique_dates = set([user_meal.created_at.strftime(DATETIME_FILTER) for user_meal in user_meals])
        min_max_dates = [
            (
                get_date_in_datetime_form(user_date),
                get_date_in_datetime_form(user_date).replace(day=get_date_in_datetime_form(user_date).day + 1)
            ) for user_date in unique_dates]
        goal_results = reduce(calculate_goal_totals_wrapper(query.filter(User.id == user_id)), min_max_dates, [])
        sorted_dates = sorted(unique_dates, key=lambda selected_date: datetime.datetime.strptime(selected_date, DATETIME_FILTER), reverse=True)

        return {
            'goal_results': goal_results,
            'dates': sorted_dates
        }

    @classmethod
    def get_meals_eaten_on_day(cls, user_id: int, user_date: str) -> dict:
        query = cls.query.join(User)
        unique_date = datetime.datetime.fromtimestamp(int(user_date) / 1000)
        min_max_dates = tuple([get_start_of_day(date) for date
         in (unique_date, unique_date.replace(day=unique_date.day + 1))])
        min_created_at, max_created_at = min_max_dates
        meals_eaten_on_day = query.filter(User.id == user_id).filter(
            Meal.created_at >= min_created_at,
            Meal.created_at < max_created_at
        )
        print(min_created_at, max_created_at)

        meals = [meal for meal in meals_eaten_on_day]
        return sorted(meals,
            key=lambda meal: meal.created_at.strftime(DATETIME_FILTER),
            reverse=True)

    @classmethod
    def find_meal(cls, user_id: int, meal_id: int) -> 'Meal':
        return cls.query.join(User).filter(
            User.id == user_id
        ).filter(cls.id == meal_id).first()

    @classmethod
    def deserialise_meals(cls, meals: Iterator[Mapping[str, Union[str, int]]]):
        return [cls(**meal) for meal in meals]

    def serialise_meal(self):
        return {
            'calories': self.calories,
            'created_at': self.created_at,
            'id': self.id,
            'meal_type': self.meal_type,
            'meal_name': self.meal_name,
            'protein': self.protein
        }
    
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
    email = db.Column(db.Text, nullable=False)
    daily_protein_goal = db.Column(db.Integer, nullable=False)
    daily_calorie_goal = db.Column(db.Integer, nullable=False)
    meals = relationship("Meal", order_by=Meal.id, back_populates="user")

    def save(self) -> tuple:
        try:
            user_data = self.find_user_by_name(self.email)
            print(user_data.daily_calorie_goal)
            if user_data is not None:
                return user_data.get_user_data(), ResultMessage.USER_ALREADY_EXISTS, True
            db.session.add(self)
            db.session.commit()
            return self.get_user_data(), ResultMessage.LOGIN_SUCCESS, True
        except Exception:
            return None, ResultMessage.LOGIN_FAILED, False

    def get_user_data(self) -> dict:
        return {
            'id': self.id,
            'email': self.email,
            'daily_calorie_goal': self.daily_calorie_goal,
            'daily_protein_goal': self.daily_protein_goal,
        }

    @classmethod
    def save_meal(cls, user_id: int, data: Iterator[Mapping[str, Union[str, int]]]):
        try:
            current_user = cls.find_user_by_id(user_id)
            meals = Meal.deserialise_meals(data['meals'])
            current_user.meals.extend(meals)
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
    def find_user_by_id(cls, user_id: int) -> 'User':
        return cls.query.filter(cls.id == user_id).first()

    @classmethod
    def find_user_by_name(cls, email: str) -> 'User':
        return cls.query.filter(cls.email == email).first()

    @classmethod
    def get_meals(cls, user_id: int, user_date: str) -> dict:
        return [meal.serialise_meal()
                for meal in Meal.get_meals_eaten_on_day(user_id, user_date)]
    
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
