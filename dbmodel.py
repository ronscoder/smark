from peewee import *
db = SqliteDatabase('./local/training.db')
from datetime import datetime

class TrainingDataModel(Model):
    created_at = DateTimeField(default=datetime.now)
    res_coeffs_0 = FloatField()
    res_coeffs_1 = FloatField()
    sup_coeffs_0 = FloatField()
    sup_coeffs_1 = FloatField()
    price_coeffs_0 = FloatField()
    price_coeffs_1 = FloatField()
    price_coeffs_2 = FloatField()
    long = IntegerField()
    short = IntegerField()
    wait = IntegerField()
    if_trained = BooleanField(default=False)
    timestamp = DateTimeField(unique=True)
    class Meta:
        database = db # This model uses the "training.db" database.

if(db.table_exists(TrainingDataModel)):
    pass
else:
    db.create_tables([TrainingDataModel])