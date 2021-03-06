from dnasearch_app.models import DnaSearch
from dnasearch_app.models import DnaSearchRequest
from rest_framework import serializers


class DnaSearchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DnaSearchRequest
        fields = [
            'search_string',
        ]


class DnaSearchSerializer(serializers.ModelSerializer):
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
