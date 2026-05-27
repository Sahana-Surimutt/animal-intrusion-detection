import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import DetectionDatabase
import json
import random

class AnalyticsEngine:
    def __init__(self):
        self.db = DetectionDatabase()
    
    def generate_insights(self, days=30):
        """Generate actionable insights from YOLO detection data"""
        stats = self.db.get_detection_stats(days)
        
        insights = []
        
        # YOLO Performance Insight
        yolo_stats = stats.get('yolo_stats', [{}])[0]
        if yolo_stats.get('overall_accuracy', 0) > 0.8:
            insights.append({
                'type': 'yolo_performance',
                'title': '🎯 YOLO Model Excellence',
                'message': f"YOLO achieving {yolo_stats.get('overall_accuracy', 0)*100:.1f}% average confidence in detections",
                'priority': 'high'
            })
        
        # Peak activity insight
        hourly_data = stats['hourly_patterns']
        if hourly_data:
            peak_hour = max(hourly_data, key=lambda x: x['count'])
            insights.append({
                'type': 'peak_activity',
                'title': '🕒 Peak Detection Hours',
                'message': f"YOLO detects most animals between {peak_hour['hour']}:00-{int(peak_hour['hour'])+1}:00",
                'priority': 'medium'
            })
        
        # Animal pattern insights
        animal_stats = stats['animal_stats']
        if animal_stats:
            most_common = animal_stats[0]
            insights.append({
                'type': 'common_animal',
                'title': '🐾 Most Frequent Detection',
                'message': f"YOLO most frequently detects {most_common['animal_type']} ({most_common['count']} times with {most_common['avg_confidence']:.1%} avg confidence)",
                'priority': 'medium'
            })
        
        # Confidence insights
        high_confidence_animals = [a for a in animal_stats if a.get('avg_confidence', 0) > 0.85]
        if high_confidence_animals:
            insights.append({
                'type': 'high_confidence',
                'title': '📈 High Accuracy Detections',
                'message': f"YOLO shows >85% confidence for {len(high_confidence_animals)} animal types",
                'priority': 'low'
            })
        
        return insights
    
    def get_prediction_models(self):
        """Get data for prediction models with YOLO focus"""
        stats = self.db.get_detection_stats(60)
        
        # Enhanced hourly predictions based on YOLO data
        hourly_patterns = {item['hour']: item['count'] for item in stats['hourly_patterns']}
        
        # Fill missing hours
        for hour in range(24):
            hour_str = f"{hour:02d}"
            if hour_str not in hourly_patterns:
                hourly_patterns[hour_str] = 0
        
        return {
            'hourly_predictions': hourly_patterns,
            'risk_levels': self.calculate_risk_levels(stats),
            'recommendations': self.generate_recommendations(stats),
            'yolo_performance': {
                'model': 'YOLOv8n',
                'accuracy': '85%+',
                'animals_detected': len(stats['animal_stats']),
                'avg_confidence': stats.get('yolo_stats', [{}])[0].get('overall_accuracy', 0.82)
            }
        }
    
    def calculate_risk_levels(self, stats):
        """Calculate risk levels based on YOLO detection patterns"""
        risk_levels = {}
        
        for animal_stat in stats['animal_stats']:
            animal = animal_stat['animal_type']
            count = animal_stat['count']
            confidence = animal_stat.get('avg_confidence', 0.5)
            
            # Enhanced risk calculation with YOLO confidence
            if animal in ['bear', 'elephant']:
                risk = 'high'
                reason = 'Large wild animal'
            elif animal in ['cow', 'horse'] and count > 10:
                risk = 'medium'
                reason = 'Large domestic animal - frequent visits'
            elif confidence > 0.9 and count > 5:
                risk = 'medium'
                reason = 'High confidence frequent detection'
            else:
                risk = 'low'
                reason = 'Normal activity'
            
            risk_levels[animal] = {
                'level': risk,
                'detections': count,
                'confidence': confidence,
                'reason': reason,
                'advice': self.get_risk_advice(animal, risk, confidence)
            }
        
        return risk_levels
    
    def get_risk_advice(self, animal, risk_level, confidence):
        """Get advice based on animal risk level and YOLO confidence"""
        advice = {
            'high': f"YOLO detected {animal} with {confidence:.1%} confidence. Activate deterrents and increase monitoring.",
            'medium': f"YOLO monitoring {animal} at {confidence:.1%} confidence. Review patterns and prepare response.",
            'low': f"YOLO tracking {animal} normally. Confidence: {confidence:.1%}. Continue standard monitoring."
        }
        
        return advice.get(risk_level, "Monitor with YOLO system")
    
    def generate_recommendations(self, stats):
        """Generate recommendations based on YOLO analytics"""
        recommendations = []
        
        # Time-based recommendations from YOLO data
        hourly_data = stats['hourly_patterns']
        if hourly_data:
            peak_hour = max(hourly_data, key=lambda x: x['count'])
            if peak_hour['count'] > 8:
                recommendations.append({
                    'type': 'timing',
                    'message': f"YOLO shows peak activity at {peak_hour['hour']}:00. Increase monitoring during this hour.",
                    'icon': '🕒'
                })
        
        # Animal-specific recommendations
        for animal_stat in stats['animal_stats'][:3]:
            if animal_stat['count'] > 5:
                recommendations.append({
                    'type': 'animal_focus',
                    'message': f"Focus on {animal_stat['animal_type']} - YOLO detected {animal_stat['count']} times with {animal_stat.get('avg_confidence', 0)*100:.1f}% confidence",
                    'icon': '🎯'
                })
        
        # YOLO performance recommendations
        yolo_stats = stats.get('yolo_stats', [{}])[0]
        if yolo_stats.get('overall_accuracy', 0) < 0.7:
            recommendations.append({
                'type': 'model_tuning',
                'message': "Consider retraining YOLO model for higher accuracy",
                'icon': '⚙️'
            })
        
        return recommendations