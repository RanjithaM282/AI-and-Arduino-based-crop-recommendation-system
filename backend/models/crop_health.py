from database.db import db
from datetime import datetime

class CropHealthAnalysis(db.Model):
    __tablename__ = 'crop_health_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    crop_cycle_id = db.Column(db.Integer, db.ForeignKey('crop_cycles.id'), nullable=False)
    photo_path = db.Column(db.String(255))
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    health_status = db.Column(db.String(50))  # healthy, disease_detected, nutrient_deficiency, pest_damage
    confidence = db.Column(db.Float)
    observation = db.Column(db.Text)
    possible_cause = db.Column(db.Text)
    recommended_action = db.Column(db.Text)
    next_inspection_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'crop_cycle_id': self.crop_cycle_id,
            'photo_path': self.photo_path,
            'analysis_date': self.analysis_date.isoformat() if self.analysis_date else None,
            'health_status': self.health_status,
            'confidence': self.confidence,
            'observation': self.observation,
            'possible_cause': self.possible_cause,
            'recommended_action': self.recommended_action,
            'next_inspection_date': self.next_inspection_date.isoformat() if self.next_inspection_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
