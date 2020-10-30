from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dnasearch.dnasearch_app.models import DnaSearch
from dnasearch.dnasearch_app.models import DnaSearchRequest
from dnasearch.dnasearch_app.serializers import DnaSearchSerializer
from dnasearch.dnasearch_app.serializers import DnaSearchRequestSerializer
from datetime import datetime

VALID_DNA_CHARS: set = {'a', 'c', 't', 'g'}

# Create your views here.

@api_view(['GET'])
def get_user_searches(request) -> Response:
    current_user_id = request.user.id
    current_user_searches = DnaSearch.objects \
        .filter(user_id=current_user_id) \
        .order_by('-started_at')
    dna_search_serializer = DnaSearchSerializer(current_user_searches, many=True)
    return Response(dna_search_serializer.data)


@api_view(['POST'])
def start_dna_search(request) -> Response:
    # validate DnaSearchRequest
    dna_search_request_serializer: DnaSearchRequestSerializer = DnaSearchRequestSerializer(request.data)

    if not dna_search_request_serializer.is_valid():
        return Response(dna_search_request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    dna_search_request: DnaSearchRequest = dna_search_request_serializer.save()

    # normalize + validate search string
    normalized_search_string = normalize_search_string(dna_search_request.search_string)

    error_response = validate_search_string(normalized_search_string)
    if error_response is not None:
        return error_response

    # transform to DnaSearch
    dna_search = DnaSearch(
        search_state=DnaSearch.SEARCH_STATES.STARTED,
        user_id=request.user.id,
        started_at=datetime.now(),
        search_string=normalized_search_string,
    )

    # enqueue to RQ first, ensuring anything in the DB is actually executing somewhere

    # write to DB
    dna_search.save()

    # return success and enqueued search
    dna_search_serializer = DnaSearchSerializer(dna_search)
    return Response(dna_search_serializer.data, status=status.HTTP_200_OK)

def normalize_search_string(search_string: str) -> str:
    return search_string.strip().lower()

def validate_search_string(search_string: str) -> Response:
    for c in search_string:
        if not c in VALID_DNA_CHARS:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    return None