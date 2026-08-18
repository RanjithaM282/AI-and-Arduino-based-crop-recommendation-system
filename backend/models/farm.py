from database.db import db
from datetime import datetime

class Farm(db.Model):
    __tablename__ = 'farms'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    name = db.Column(db.String(100))
    size_acres = db.Column(db.Float, nullable=False)
    soil_type = db.Column(db.String(50), nullable=False)
    irrigation_type = db.Column(db.String(50), nullable=False)
    current_crop = db.Column(db.String(50))
    previous_crops = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    crop_cycles = db.relationship('CropCycle', backref='farm', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('FarmActivity', backref='farm', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'farmer_id': self.farmer_id,
            'name': self.name,
            'size_acres': self.size_acres,
            'soil_type': self.soil_type,
            'irrigation_type': self.irrigation_type,
            'current_crop': self.current_crop,
            'previous_crops': self.previous_crops,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
