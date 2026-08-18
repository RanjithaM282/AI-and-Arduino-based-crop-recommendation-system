from database.db import db
from datetime import datetime

class FarmActivity(db.Model):
    __tablename__ = 'farm_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    crop_cycle_id = db.Column(db.Integer, db.ForeignKey('crop_cycles.id'))
    activity_type = db.Column(db.String(50), nullable=False)  # irrigation, fertilization, pesticide, weeding, harvesting
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float)  # quantity of fertilizer, pesticide, etc.
    cost = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'crop_cycle_id': self.crop_cycle_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'amount': self.amount,
            'cost': self.cost,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
