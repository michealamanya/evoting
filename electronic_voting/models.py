from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_date:
            return "Upcoming"
        elif now <= self.end_date:
            return "Ongoing"
        else:
            return "Completed"

class Position(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='positions')
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.title} - {self.election.title}"

class Candidate(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField()
    photo = models.ImageField(upload_to='candidate_photos/', null=True, blank=True)
    manifesto = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.position.title}"
    
    @property
    def vote_count(self):
        return self.votes.count()

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='votes')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('voter', 'position', 'election')
        
    def __str__(self):
        return f"{self.voter.username} voted for {self.candidate.user.username}"
