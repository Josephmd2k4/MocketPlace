from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from webpush import send_user_notification
import json
from django.conf import settings

@require_GET # decorator that only allows get requests
def home(request):
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY') # gets vpk from the obj to send to client, checked against priv key for security purposes
    user = request.user # incoming requests get their user info saved here 
    return render(request, 'notifHome.html', {user: user, 'vapid_key': vapid_key})

# restricts view to post requests only,
# exempts view from CrossSiteRequestForgery protection,
# expects post data, gets request body, and converts JSON doc to py
@require_POST 
@csrf_exempt
def send_push(request):
    try:  
        body = request.body
        data = json.loads(body)
    # head = notif title, body = notif contents, id = requesting user's id
        if 'head' not in data or 'body' not in data or 'id' not in data:
            return JsonResponse(status=400, data={"message": "Invalid data format"})
    # if anything is missing 404 is given, otherwise returns a matching pk w get_object_or_404
        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)
        payload = {'head': data['head'], 'body': data['body']}
        send_user_notification(user=user, payload=payload, ttl=1000)
    # here user=recipient of notif, pld=notif info(head&body), ttl=max seconds notif should be stored

        return JsonResponse(status=200, data={"message": "Web push successful"})
    # return success status
    except TypeError:
        return JsonResponse(status=500, data={"message": "An error occurred"})
