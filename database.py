from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DataSensor(db.Model):
    __tablename__ = 'DataSensor'

    id = db.Column(db.Integer, primary_key=True)
    equipmentId = db.Column(db.String(255),nullable = False)
    timestamp = db.Column(db.DateTime,nullable = False)
    value = db.Column(db.Numeric(precision=10, scale=2),nullable = True)

