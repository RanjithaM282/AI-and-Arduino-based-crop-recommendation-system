from database.db import db
from datetime import datetime

class CropCycle(db.Model):
    __tablename__ = 'crop_cycles'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    crop_name = db.Column(db.String(50), nullable=False)
    planting_date = db.Column(db.Date, nullable=False)
    expected_harvest_date = db.Column(db.Date)
    actual_harvest_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='planted')  # planted, growing, harvested
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('FarmActivity', backref='crop_cycle', lazy=True)
    health_analyses = db.relationship('CropHealthAnalysis', backref='crop_cycle', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'crop_name': self.crop_name,
            'planting_date': self.planting_date.isoformat() if self.planting_date else None,
            'expected_harvest_date': self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            'actual_harvest_date': self.actual_harvest_date.isoformat() if self.actual_harvest_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
