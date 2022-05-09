from training_data import TrainingDataModel, TrainingDataModel2
from peewee import *
db = SqliteDatabase('./data/training.db')

db.create_tables([TrainingDataModel2])


for r in TrainingDataModel.select():
    r2 = TrainingDataModel2(res_coeffs_0 = r.res_coeffs_0,
            res_coeffs_1=r.res_coeffs_1, sup_coeffs_0 = r.sup_coeffs_0, sup_coeffs_1=r.sup_coeffs_1, price_coeffs_0 = r.price_coeffs_0, price_coeffs_1 = r.price_coeffs_1, price_coeffs_2 = r.price_coeffs_2, long=1 if r.direction==1 else 0, short=1 if r.direction == -1 else 0, wait = 1 if r.direction ==0 else 0)
    r2.save()