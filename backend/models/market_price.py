from database.db import db
from datetime import datetime

class MarketPrice(db.Model):
    __tablename__ = 'market_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(50), nullable=False)
    market_name = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    modal_price = db.Column(db.Float, nullable=False)
    min_price = db.Column(db.Float, nullable=False)
    max_price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='Quintal')
    price_date = db.Column(db.Date, nullable=False)
    arrival_quantity = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'crop_name': self.crop_name,
            'market_name': self.market_name,
            'district': self.district,
            'state': self.state,
            'modal_price': self.modal_price,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'unit': self.unit,
            'price_date': self.price_date.isoformat() if self.price_date else None,
            'arrival_quantity': self.arrival_quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
