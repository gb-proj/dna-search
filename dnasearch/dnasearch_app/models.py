from django.db import models
from django.contrib import auth


class DnaSearchRequest(models.Model):
    search_string = models.TextField()

# Create your models here.
class DnaSearch(models.Model):
    # represents the status of the current async search
    # Starts in SEARCHING -> terminates in FOUND, NOT_FOUND, or ERROR depending on result
    SEARCH_STATES = (
        ('SEARCHING', 'Searching'),
        ('FOUND', 'Found'),
        ('NOT_FOUND', 'Not found'),
        ('ERROR', 'Error'),
    )

    search_state = models.CharField(max_length=16, choices=SEARCH_STATES)

    user_id = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)
    started_at = models.DateTimeField('datetime search was started')
    completed_at = models.DateTimeField('datetime search was completed', null=True)

    search_string = models.TextField()

    result_protein = models.TextField(null=True)
    result_start_location = models.IntegerField(null=True)
    result_end_location = models.IntegerField(null=True)
