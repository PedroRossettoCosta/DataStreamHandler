from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DataSensor(db.Model):
    __tablename__ = 'data_sensor'

    ID = db.Column(db.Integer, primary_key=True)
    equipmentId = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)
    value = db.Column(db.Numeric(precision=10, scale=2))