from django.db import models
from django.contrib.auth.models import User
from electronic_voting.models import Election, Position, Candidate, Vote

class AnalyticsReport(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    
    def __str__(self):
        return f"{self.title} - {self.election.title}"

class VotingStatistic(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='statistics')
    timestamp = models.DateTimeField(auto_now_add=True)
    total_votes = models.IntegerField(default=0)
    unique_voters = models.IntegerField(default=0)
    participation_rate = models.FloatField(default=0.0)  # percentage
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Stats for {self.election.title} at {self.timestamp}"
