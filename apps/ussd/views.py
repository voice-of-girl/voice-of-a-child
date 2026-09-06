import logging
import re

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .services import UssdService

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def ussd_callback(request):
    """Africa's Talking callback endpoint. Always returns plain text CON/END output."""
    session_id = request.POST.get('sessionId', '')
    phone_number = request.POST.get('phoneNumber', '')
    service_code = request.POST.get('serviceCode', '')
    network_code = request.POST.get('networkCode', '')
    text = request.POST.get('text', '')

    if not session_id or not phone_number or not re.fullmatch(r'\+?[0-9]{7,15}', phone_number):
        return HttpResponse('END We could not identify this session. Please try again.', content_type='text/plain', status=400)

    throttle_key = f'ussd-rate:{phone_number}'
    calls = cache.get(throttle_key, 0)
    if calls >= getattr(settings, 'USSD_MAX_CALLS_PER_MINUTE', 30):
        return HttpResponse('END Too many requests. Please try again shortly.', content_type='text/plain', status=429)
    cache.set(throttle_key, calls + 1, timeout=60)

    logger.info('USSD callback received: session=%s phone_suffix=%s text_length=%s', session_id[-8:], phone_number[-4:], len(text))
    response = UssdService(session_id, phone_number, service_code, network_code).handle(text)
    return HttpResponse(response, content_type='text/plain')
