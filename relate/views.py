import json
import ripple.api as ripple
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.http import JsonResponse
from general.util import render
from django.shortcuts import render as django_render
from profile.models import Profile
from relate.forms import EndorseForm, AcknowledgementForm, BlankTrust, BlankPaymentForm
from relate.models import Endorsement, Referral
from notification.models import Notification
from notification.utils import create_notification
from general.mail import send_notification
from django.utils.translation import ugettext as _
from feed.models import FeedItem
from django.contrib.gis.db.models import Q
from django.templatetags.static import static


MESSAGES = {
    'endorsement_saved': _("Trust saved."),
    'endorsement_deleted': _("Trust deleted."),
    'acknowledgement_sent': _("Payment sent."),
}


def trust_ajax(request, recipient_username):
    data = {}
    recipient = get_object_or_404(Profile, user__username=recipient_username)
    if recipient == request.profile:
        data['stat'] = 'error'
        data['error_message'] = 'You cannot send a trust to yourself'
        return JsonResponse({'data': data})
    try:
        endorsement = Endorsement.objects.get(endorser=request.profile, recipient=recipient)

        referral = Referral.objects.filter(referrer=endorsement.endorser, recipient=endorsement.recipient)

        data['weight'] = endorsement.weight
        data['text'] = endorsement.text
        data['recipient'] = recipient_username
        if referral:
            data['refer'] = True
        data['stat'] = 'existing'
    except Endorsement.DoesNotExist:
        data['stat'] = "ok"
    return JsonResponse({'data': data})


def endorse_user(request, recipient_username):
    data = {}
    recipient = get_object_or_404(Profile, user__username=recipient_username)
    if recipient == request.profile:
        data['error'] = 'Logged profile and recipient are the same'
        return JsonResponse({'data': data})
    try:
        endorsement = Endorsement.objects.get(
            endorser=request.profile, recipient=recipient)
    except Endorsement.DoesNotExist:
        endorsement = None
    if request.method == 'POST':
        if 'delete' in request.POST and endorsement:
            endorsement.delete()
            messages.info(request, MESSAGES['endorsement_deleted'])
            return HttpResponseRedirect(
                endorsement.recipient.get_absolute_url())
        form = EndorseForm(request.POST, instance=endorsement,
                           endorser=request.profile, recipient=recipient)
        if form.is_valid():
            endorsement = form.save()
            create_notification(notifier=request.profile, recipient=recipient, type=Notification.TRUST)
            if form.cleaned_data['referral']:
                existing_referral = Referral.objects.filter(referrer=request.profile, recipient=recipient)
                if not existing_referral:
                    new_referral = Referral()
                    new_referral.referrer = request.profile
                    new_referral.recipient = recipient
                    new_referral.save()

                    new_referral_count = FeedItem.objects.filter(item_type='profile', poster=recipient)[0].referral_count + 1
                    FeedItem.objects.filter(poster=recipient, item_type='profile').\
                        update(referral_count=new_referral_count)
            send_endorsement_notification(endorsement)
            messages.info(request, MESSAGES['endorsement_saved'])
            data['recipient'] = recipient_username
            data['stat'] = 'ok'
            return JsonResponse({'data': data})
        else:
            data['stat'] = 'error'
            data['errors'] = form.errors
            return JsonResponse({'data': data})

    else:
        form = EndorseForm(instance=endorsement, endorser=request.profile,
                           recipient=recipient)
    profile = recipient  # For profile_base.html.
    return django_render(request, 'frontend/home.html', {'form': form})


def acknowledge_user_ajax(request, recipient_username):
    data = {}
    recipient = get_object_or_404(Profile, user__username=recipient_username)
    if recipient == request.profile:
        data['stat'] = 'You cannot send a payment to yourself'
        return JsonResponse({'data': data})
    else:
        max_amount = ripple.max_payment(request.profile, recipient)
        can_ripple = max_amount > 0
        data['stat'] = 'ok'
        data['can_ripple'] = can_ripple
        data['max_amount'] = max_amount
        data['recipient'] = recipient_username
        return JsonResponse({'data': data})


def send_endorsement_notification(endorsement):
    subject = _("%s has endorsed you on Villages.io") % endorsement.endorser
    send_notification(subject, endorsement.endorser, endorsement.recipient,
                      'endorsement_notification_email.txt',
                      {'endorsement': endorsement})

@login_required
@render()
def endorsement(request, endorsement_id):
    endorsement = get_object_or_404(Endorsement, pk=endorsement_id)
    return locals()
    
@login_required
@render()
def relationships(request):
    accounts = ripple.get_user_accounts(request.profile)
    return locals()

@login_required
@render()
def relationship(request, partner_username):
    partner = get_object_or_404(Profile, user__username=partner_username)
    if partner == request.profile:
        raise Http404  # Can't have relationship with yourself.
    account = request.profile.account(partner)
    if account:
        entries = account.entries 
        balance = account.balance
    else:
        entries = []
        balance = 0
    profile = partner  # For profile_base.html.
    return locals()

@login_required
@render()
def acknowledge_user(request, recipient_username):
    recipient = get_object_or_404(Profile, user__username=recipient_username)
    if recipient == request.profile:
        raise Http404
    # TODO: Don't recompute max_amount on form submit?  Cache, or put in form
    # as hidden field?
    max_amount = ripple.max_payment(request.profile, recipient)
    if request.method == 'POST':
        form = AcknowledgementForm(request.POST, max_ripple=max_amount)
        if form.is_valid():
            acknowledgement = form.send_acknowledgement(
                request.profile, recipient)
            create_notification(notifier=request.profile, recipient=recipient, type=Notification.PAYMENT)
            # send_acknowledgement_notification(acknowledgement)
            messages.info(request, MESSAGES['acknowledgement_sent'])
            return HttpResponseRedirect(acknowledgement.get_absolute_url())
    else:
        form = AcknowledgementForm(max_ripple=max_amount, initial=request.GET)
    can_ripple = max_amount > 0
    profile = recipient  # For profile_base.html.
    return locals()


def pay_user_ajax(request, recipient_username):
    data = {}
    recipient = get_object_or_404(Profile, user__username=recipient_username)
    if recipient == request.profile:
        raise Http404
    # TODO: Don't recompute max_amount on form submit?  Cache, or put in form
    # as hidden field?
    max_amount = ripple.max_payment(request.profile, recipient)
    if request.method == 'POST':
        form = AcknowledgementForm(request.POST, max_ripple=max_amount)
        if form.is_valid():
            acknowledgement = form.send_acknowledgement(
                request.profile, recipient)
            create_notification(notifier=request.profile, recipient=recipient, type=Notification.PAYMENT)
            has_referral = Referral.objects.filter(referrer=request.profile, recipient=recipient).all()
            send_acknowledgement_notification(acknowledgement)
            messages.info(request, MESSAGES['acknowledgement_sent'])
            data['stat'] = 'ok'
            data['recipient'] = recipient_username
            data['refer'] = True if has_referral else False
            return JsonResponse({'data': data})
        else:
            data['stat'] = 'error'
            data['errors'] = form.errors
            return JsonResponse({'data': data})
    else:
        form = AcknowledgementForm(max_ripple=max_amount, initial=request.GET)
    data['stat'] = 'error'
    return JsonResponse({'data': data})


def send_acknowledgement_notification(acknowledgement):
    subject = _("%s has acknowledged you on Villages.io") % (
        acknowledgement.payer)
    send_notification(subject, acknowledgement.payer, acknowledgement.recipient,
                      'acknowledgement_notification_email.txt',
                      {'acknowledgement': acknowledgement})


@login_required
@render()
def view_acknowledgement(request, payment_id):
    try:
        payment = ripple.get_payment(payment_id)
    except ripple.RipplePayment.DoesNotExist:
        raise Http404
    entries = payment.entries_for_user(request.profile)
    if not entries:
        raise Http404  # Non-participants don't get to see anything.
    sent_entries = []
    received_entries = []
    for entry in entries:
        if entry.amount < 0:
            sent_entries.append(entry)
        else:
            received_entries.append(entry)
    return locals()


def get_user_photo(request, profile_username):
    """
    This method is used to catpure user_photo path, payment list summary and max trust amount in payments
    :param request:
    :param profile_id:
    :return:
    """
    data = {}
    payments = []
    profile = Profile.objects.get(user__username=profile_username)
    if profile == request.profile:
        data['error'] = "same_user"
        data['error_message'] = "You can't send a trust to yourself"
        return JsonResponse({'data': data})
    payment_list = FeedItem.objects.filter(poster_id=request.profile.id, recipient_id=profile.id).all()
    recipient = get_object_or_404(Profile, id=profile.id)
    try:
        trust = Endorsement.objects.get(endorser=request.profile, recipient=recipient)
    except Endorsement.DoesNotExist:
        trust = None
    max_amount = ripple.max_payment(request.profile, recipient)
    can_ripple = max_amount > 0
    if payment_list:
        for each_payment in payment_list:
            payments.append('{0} paid {1} in {2}'.format(each_payment.poster.name, each_payment.recipient.name, each_payment.date.date()))
    if trust:
        refer = Referral.objects.filter(referrer=request.profile, recipient=recipient)
        if refer:
            data['refer'] = True
        data['has_trust'] = True
        data['credit_limit'] = trust.weight
        data['text'] = trust.text
        data['updated'] = trust.updated
    if not profile.photo:
        profile_photo_path = static('img/generic_user.png')
    else:
        profile_photo_path = '/uploads/'+str(profile.photo)
    data['profile_photo_path'] = profile_photo_path
    data['payment_list'] = payments
    data['max_amount'] = max_amount
    data['can_ripple'] = can_ripple
    data['recipient'] = recipient.name
    return JsonResponse({'data': data})


def get_recipients_data(request):
    if request.is_ajax() and request.method == 'GET':
        result = []
        if not request.GET['query']:
            recipient_info = Profile.objects.all()[:50]
        else:
            recipient_info = Profile.objects.filter(Q(name__icontains=request.GET['query']) |
                                                    Q(user__username__icontains=request.GET['query']))
        for recipient in recipient_info:
            result.append({'name': recipient.name, 'profile_id': recipient.id,
                           'username': recipient.username})
        return JsonResponse({'result': result})


@login_required
@render()
def blank_trust(request):
    profile = request.profile

    if request.method == 'GET':
        endorsement = None
        referral = False
        form_errors = {}

        recipient_name = request.GET.get('recipient_name')
        if recipient_name:
            try:
                recipient = Profile.objects.get(user__username=recipient_name)
            except Profile.DoesNotExist:
                form_errors['recipient_name'] = "Recipient doesn't exist"
            else:
                referral = Referral.objects.filter(referrer=profile, recipient=recipient).exists()
                try:
                    endorsement = Endorsement.objects.get(endorser=profile, recipient=recipient)
                except Endorsement.DoesNotExist:
                    pass

        form = BlankTrust(instance=endorsement, initial={'recipient_name': recipient_name, 'referral': referral})
        for field_name, error_message in form_errors.iteritems():
            form.errors[field_name] = error_message

    elif request.method == 'POST':
        if not request.POST['recipient_name']:
            messages.add_message(request, messages.ERROR, 'The recipient is invalid, please verify')
        else:
            recipient = get_object_or_404(Profile, user__username=request.POST['recipient_name'])
            if recipient == profile:
                messages.add_message(request, messages.ERROR, 'You cant send a trust to yourself')
            else:
                try:
                    endorsement = Endorsement.objects.get(endorser=profile, recipient=recipient)
                except Endorsement.DoesNotExist:
                    endorsement = None
                if 'delete' in request.POST and endorsement:
                    # TODO implement logic for delete trust
                    endorsement.delete()
                    messages.add_message(request, messages.INFO, 'Trust deleted')
                else:
                    form = BlankTrust(request.POST, instance=endorsement, endorser=profile, recipient=recipient)
                    if form.is_valid():
                        endorsement = form.save()
                        create_notification(notifier=profile, recipient=recipient, type=Notification.TRUST)
                        existing_referral = Referral.objects.filter(referrer=profile, recipient=recipient)
                        if form.cleaned_data['referral']:
                            if not existing_referral:
                                Referral.objects.create(referrer=profile, recipient=recipient)
                        else:
                            if existing_referral:
                                existing_referral.delete()
                        send_endorsement_notification(endorsement)
                        messages.add_message(request, messages.INFO, 'Trust saved!')

    accounts = ripple.get_user_accounts(request.profile)
    return django_render(request, 'new_templates/trust.html', {'form': form, 'accounts': accounts, 'profile': profile})


@login_required()
def blank_payment(request):
    profile = request.profile

    if request.method == 'GET':
        recipient = None
        max_amount = 0
        form_errors = {}

        recipient_name = request.GET.get('recipient_name')
        if recipient_name:
            try:
                recipient = Profile.objects.get(user__username=recipient_name)
            except Profile.DoesNotExist:
                form_errors['recipient'] = "Recipient doesn't exist"
            else:
                max_amount = ripple.max_payment(profile, recipient)

        form = BlankPaymentForm(payer=profile, recipient=recipient, max_amount=max_amount,
                                initial={'recipient': request.GET.get('recipient_name'),
                                         'amount': request.GET.get('amount'),
                                         'memo': request.GET.get('memo')})
        for field_name, error_message in form_errors.iteritems():
            form.errors[field_name] = error_message
    if request.method == 'POST':
        if not request.POST['recipient']:
            messages.add_message(request, messages.ERROR, 'The recipient is invalid, please verify')
        else:
            recipient = get_object_or_404(Profile, user__username=request.POST['recipient'])
            max_amount = ripple.max_payment(profile, recipient)
            form = BlankPaymentForm(request.POST, payer=profile, recipient=recipient, max_amount=max_amount)
            if form.is_valid():
                if recipient == profile:
                    messages.add_message(request, messages.ERROR, 'You cant send a payment to yourself')
                    form.errors['recipient'] = 'Choose another recipient.'
                else:
                    payment = form.send_payment()
                    create_notification(notifier=profile, recipient=recipient, type=Notification.PAYMENT)
                    send_payment_notification(payment)
                    messages.add_message(request, messages.INFO,
                                         'Payment sent {}.'.format('through the trust network'
                                                                   if form.cleaned_data['routed'] else 'directly'))

    all_payments = FeedItem.objects.filter((Q(recipient_id=profile.id) | Q(poster_id=profile.id)) & Q(item_type='acknowledgement')).order_by('-date')
    return django_render(request, 'new_templates/pay.html', {'form': form, 'all_payments': all_payments})


def send_payment_notification(payment):
    subject = _("%s has acknowledged you on Villages.io") % (
        payment.payer)
    send_notification(subject, payment.payer, payment.recipient,
                      'acknowledgement_notification_email.txt',
                      {'acknowledgement': payment})


def get_profiles(request):
    # what was in the question an array is now a python list of dicts.
    # it can also be in some other file and just imported.
    if request.is_ajax():
        q = request.GET.get('term', '')

        profiles = Profile.objects.exclude(pk=request.profile.id).filter(name__icontains=q)[:20]
        results = []
        for profile in profiles:
            profile_json = {}
            profile_json['id'] = profile.id
            profile_json['label'] = profile.name
            profile_json['value'] = profile.name
            results.append(profile_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def referral_on_payment(request):
    result = {}
    if request.method == 'POST' and request.is_ajax():
        recipient = json.loads(request.body)
        recipient = get_object_or_404(Profile, user__username=recipient['profile'])
        new_referral = Referral()
        new_referral.recipient = recipient
        new_referral.referrer = request.profile
        new_referral.save()
        result['success'] = True
        return JsonResponse({'result': result})
