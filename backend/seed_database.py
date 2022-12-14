import sqlalchemy
import MySQLdb

import models
import app as server_app


app = server_app.create_app()

models.db.init_app(app)
with app.app_context():

    try:
        models.Meal.__table__.drop(models.db.engine)
        models.User.__table__.drop(models.db.engine)
    except (sqlalchemy.exc.ProgrammingError, MySQLdb.ProgrammingError):
        pass

    models.db.create_all()
    
    u1 = models.User(email='Bob@mail.com', daily_protein_goal=100, daily_calorie_goal=2000)
    u2 = models.User(email='Ant@mail.com', daily_calorie_goal=2500, daily_protein_goal=80)

    m1 = models.Meal(meal_name="Cereal", meal_type='Food', calories=100, protein=100, user=u1)
    m2 = models.Meal(meal_name="Cereal", meal_type='Drink', calories=300, protein=10, user=u1)
    m3 = models.Meal(meal_name="Cereal", meal_type='Food', calories=100, protein=100, user=u1)
    m4 = models.Meal(meal_name="Cereal", meal_type='Drink', calories=250, protein=30, user=u1)
    m5 = models.Meal(meal_name="Cereal", meal_type='Food', calories=100, protein=100, user=u2)
    m6 = models.Meal(meal_name="Cereal", meal_type='Drink', calories=500, protein=50, user=u2)
    m7 = models.Meal(meal_name="Cereal", meal_type='Drink', calories=50, protein=5, user=u2)
    m8 = models.Meal(meal_name="Cereal", meal_type='Food', calories=100, protein=80, user=u2)

    models.db.session.add_all([u1, u2])
    models.db.session.add_all([m1, m2, m3, m4, m5, m6, m7, m8])
    models.db.session.commit()
    
    print('DB seeded successfully!')