from app import db
from flask_login import LoginManager, UserMixin



class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_agent = db.Column(db.Boolean, default=False)
    properties = db.relationship('Property', secondary='user_property', back_populates='users')
   
user_property = db.Table('user_property',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('property_id', db.Integer, db.ForeignKey('property.id'), primary_key=True)
)

class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(150), nullable=True)
    price = db.Column(db.Float, nullable=False)
    num_of_rooms = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    users = db.relationship('User', secondary=user_property, back_populates='properties')
    images = db.relationship('Image', backref='property', lazy=True)     

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    filepath = db.Column(db.String(200), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)