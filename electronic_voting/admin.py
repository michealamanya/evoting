from django.contrib import admin
from .models import Election, Position, Candidate, Vote

class PositionInline(admin.TabularInline):
    model = Position
    extra = 1

class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'status')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    inlines = [PositionInline]
    
    def status(self, obj):
        return obj.status

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'election')
    list_filter = ('election',)
    search_fields = ('title', 'description')
    inlines = [CandidateInline]

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'vote_count')
    list_filter = ('position__election', 'position')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'bio')
    
    def vote_count(self, obj):
        return obj.vote_count

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'candidate', 'position', 'election', 'timestamp')
    list_filter = ('election', 'position', 'timestamp')
    search_fields = ('voter__username', 'candidate__user__username')
    date_hierarchy = 'timestamp'
