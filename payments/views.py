from django.shortcuts import render
import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.templatetags.static import static
from posts.views import login_required
from .forms import PaymentForm
from posts.models import Post, Media

def payment_view(request, post_id, media_file=None):
    post = get_object_or_404(Post, id=post_id)
    title = post.title
    price = post.price
    desc = post.description

    # If media_file parameter was provided and not default, try to use it
    if media_file and media_file != 'default.jpg':
        try:
            media = Media.objects.get(file=media_file)
            media_to_display = media.file.url
        except Media.DoesNotExist:
            # If specified media doesn't exist, fall back to first media or default
            media = post.media.first()
            if media and media.file_url:
                media_to_display = media.file_url
            else:
                media_to_display = static('images/default.jpg')
    else:
        # If no media_file specified or it's default, use first media or default
        media = post.media.first()
        if media and media.file_url:
            media_to_display = media.file_url
        else:
            media_to_display = static('images/default.jpg')

    return render(request, "payments/checkout.html", {
        'title': title,
        'price': price,
        'post': post,
        'description': desc,
        'media': media_to_display,
    })

@csrf_exempt
def payment_success_view(request):
    return HttpResponse("Payment successful!")

@csrf_exempt
def payment_cancel_view(request):
    return HttpResponse("Payment cancelled.")
