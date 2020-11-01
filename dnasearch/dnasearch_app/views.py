import django_rq
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dnasearch_app.models import DnaSearch
from dnasearch_app.models import DnaSearchRequest
from dnasearch_app.serializers import DnaSearchSerializer
from dnasearch_app.serializers import DnaSearchRequestSerializer
from datetime import datetime
from dnasearch_app.dna_search_task import dna_search_task

VALID_DNA_CHARS: set = {'A', 'C', 'T', 'G'}


# Create your views here.

@api_view(['GET'])
def get_user_searches(request) -> Response:
    current_user_id = request.user.id
    current_user_searches = DnaSearch.objects \
        .filter(user_id=current_user_id) \
        .order_by('-started_at')

    dna_search_serializer = DnaSearchSerializer(current_user_searches, many=True, context={'request': request})

    # if not dna_search_serializer.is_valid():
    # this should never happen, indicates mismatch between DB, model, and Serializer
    # return Response(dna_search_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(dna_search_serializer.data)


@api_view(['POST'])
def start_dna_search(request) -> Response:
    # validate DnaSearchRequest
    dna_search_request_serializer: DnaSearchRequestSerializer = DnaSearchRequestSerializer(data=request.data)

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
        search_state='SEARCHING',
        user_id=request.user,
        started_at=datetime.now(),
        search_string=normalized_search_string,
    )

    # write to DB first so we can have an ID to hand to RQ
    dna_search.save()

    # enqueue to RQ
    queue = django_rq.get_queue('default', autocommit=True, is_async=True, default_timeout=360)
    queue.enqueue(dna_search_task, dna_search)

    # return success and enqueued search
    dna_search_serializer = DnaSearchSerializer(dna_search, context={'request': request})
    return Response(dna_search_serializer.data, status=status.HTTP_200_OK)


def normalize_search_string(search_string: str) -> str:
    return search_string.strip().upper()


def validate_search_string(search_string: str) -> Response:
    for c in search_string:
        if not c in VALID_DNA_CHARS:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    return None
