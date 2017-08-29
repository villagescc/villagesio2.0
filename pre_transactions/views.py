from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from notification.utils import create_notification
from notification.models import Notification
from feed.models import FeedItem
from relate.models import Endorsement
from profile.models import Profile
import ripple.api as ripple


def trust(request):
    if not request.profile:
        messages.add_message(request, messages.WARNING, 'You must be logged in to send this trust')
        return render(request, 'pre_trust.html')

    username = request.GET.get('username')
    weigth = request.GET.get('weigth')
    text = request.GET.get('text')

    if not username or not weigth:
        messages.add_message(request, messages.ERROR, 'Invalid parameters, please verify')
        return render(request, 'pre_trust.html')

    try:
        recipient = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'The user is invalid')
        return render(request, 'pre_trust.html')
    if recipient == request.profile:
        messages.add_message(request, messages.WARNING, "You can't send a trust to yourself" )
        return render(request, 'pre_trust.html')
    else:
        if request.method == 'POST':
            endorsement = Endorsement.objects.get(endorser=request.profile, recipient=recipient)
            if endorsement:
                if text:
                    endorsement.text = text
                if weigth:
                    endorsement.weight = weigth
                endorsement.save()
                create_notification(notifier=request.profile, recipient=recipient, type=Notification.TRUST)
            else:
                new_trust = Endorsement()
                new_trust.endorser = request.profile
                new_trust.recipient = recipient
                new_trust.weight = weigth
                new_trust.text = text
                new_trust.save()
                create_notification(notifier=request.profile, recipient=recipient, type=Notification.TRUST)
            messages.add_message(request, messages.SUCCESS, 'Successfully sent trust')
            return HttpResponseRedirect(reverse('frontend:home'))
        else:
            endorsement = Endorsement.objects.filter(endorser=request.profile, recipient=recipient).all()
            if endorsement:
                endorsement = endorsement[0]
                return render(request, 'pre_trust.html',
                              {'recipient': endorsement.recipient, 'endorser': endorsement.endorser,
                               'weigth': endorsement.weight, 'text': endorsement.text, 'endorsement_exists': True})
            else:
                return render(request, 'pre_trust.html', {'recipient': recipient, 'weigth': weigth, 'text': text,
                                                          'endorsement_exists': True})


def pay(request):
    if not request.profile:
        messages.add_message(request, messages.WARNING, 'You must be logged in to send this trust')
        return render(request, 'pre_payment.html')

    username = request.GET.get('username')
    hours = request.GET.get('hours')
    text = request.GET.get('text')

    if not username or not hours:
        messages.add_message(request, messages.ERROR, 'Invalid parameters, please verify')
        return render(request, 'pre_payment.html')

    try:
        recipient = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'The user is invalid')
        return render(request, 'pre_payment.html')
    if recipient == request.profile:
        messages.add_message(request, messages.WARNING, "You can't send a trust to yourself")
        return render(request, 'pre_payment.html')
    else:
        if request.method == 'POST':
            payment_type = request.POST.get('ripple')

            if text:
                text = text.encode('UTF-8')
            if hours:
                hours = hours.encode('UTF-8')
            if payment_type:
                payment_type = payment_type.encode('UTF-8')

            send_payment(request.profile, recipient, float(hours), text, payment_type)
            create_notification(notifier=request.profile, recipient=recipient, type=Notification.PAYMENT)
            messages.add_message(request, messages.SUCCESS, 'Successfully sent payment')
            return HttpResponseRedirect(reverse('frontend:home'))

        else:
            max_amount = ripple.max_payment(request.profile, recipient)
            can_ripple = max_amount > 0
            return render(request, 'pre_payment.html', {'recipient': recipient, 'hours': hours, 'text': text,
                                                        'can_ripple': can_ripple, 'max_amount': max_amount})


def send_payment(payer, recipient, hours, text, payment_type):

    ROUTED = 'routed'
    DIRECT = 'direct'

    routed = payment_type == ROUTED
    obj = ripple.pay(
        payer, recipient, hours, text, routed=routed)
    # Create feed item
    FeedItem.create_feed_items(
        sender=ripple.RipplePayment, instance=obj, created=True)
    return obj
