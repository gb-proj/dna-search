from dnasearch.dnasearch_app.models import DnaSearch, DnaSearchRequest
from rest_framework import serializers

class DnaSearchRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DnaSearchRequest
        fields = [
            'search_string',
        ]

class DnaSearchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DnaSearch
        fields = [
            'search_state',
            'user_id',
            'started_at',
            'completed_at',
            'search_string',
            'result_protein',
            'result_start_location',
            'result_end_location',
        ]