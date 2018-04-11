import ujson
from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
# Forms
from accounts.forms import UserForm
from listings.forms import ListingsForms
from listings.models import LISTING_TYPE_CHECK
from feed.forms import FeedFilterForm, DATE_FORMAT
from notification.models import Notification
from relate.forms import EndorseForm, AcknowledgementForm
from profile.forms import ContactForm
from frontend.forms import FormListingsSettings
from django_user_agents.utils import get_user_agent
from profile.templatetags.profile import *
# models
from listings.models import Listings
from categories.models import Categories, SubCategories

TRUSTED_SUBQUERY = (
    "feed_feeditem.poster_id in "
    "(select to_profile_id from profile_profile_trusted_profiles "
    "    where from_profile_id = %s)")

LISTINGS_TRUSTED_QUERY = (
    """"select listings_listings.id from listings_listings inner join profile_profile on (listings_listings.user_id = profile_profile.user_id) where profile_profile.id in (select profile_profile_trusted_profiles.to_profile_id from profile_profile_trusted_profiles where profile_profile_trusted_profiles.from_profile_id = {0})""")

SUBQUERY = (
    "profile_profile.id in "
    "(select profile_profile_trusted_profiles.to_profile_id from profile_profile_trusted_profiles "
    "where profile_profile_trusted_profiles.from_profile_id = %s)")


def listing_type_filter(request, listing_type):
    """
    :param request:
    :param category_type:
    :return:
    """
    listing_type_objects = Listings.objects.all().filter(listing_type=listing_type).order_by('-created')
    form = ListingsForms()
    form_listing_settings = FormListingsSettings(initial=request.GET)
    categories_list = Categories.objects.all()
    item_sub_categories = SubCategories.objects.all().filter(categories=1)
    services_sub_categories = SubCategories.objects.all().filter(categories=2)
    rideshare_sub_categories = SubCategories.objects.all().filter(categories=3)
    housing_sub_categories = SubCategories.objects.all().filter(categories=4)
    return render(request, 'frontend/home.html', {'listing_form': form, 'listings': listing_type_objects,
                                                  'item_sub_categories': item_sub_categories,
                                                  'services_sub_categories': services_sub_categories,
                                                  'rideshare_sub_categories': rideshare_sub_categories,
                                                  'housing_sub_categories': housing_sub_categories,
                                                  'categories': categories_list, 'listing_type_filter': listing_type,
                                                  'form_listing_settings': form_listing_settings, 'is_listing': True})


def categories_filter(request, category_type):
    """
    :param request:
    :param category_type:
    :return:
    """
    listing_type_objects = Listings.objects.all().filter(subcategories__categories__categories_text=category_type).order_by('-created')
    form = ListingsForms()
    form_listing_settings = FormListingsSettings(initial=request.GET)
    categories_list = Categories.objects.all()
    item_sub_categories = SubCategories.objects.all().filter(categories=1)
    services_sub_categories = SubCategories.objects.all().filter(categories=2)
    rideshare_sub_categories = SubCategories.objects.all().filter(categories=3)
    housing_sub_categories = SubCategories.objects.all().filter(categories=4)
    return render(request, 'frontend/home.html', {'listing_form': form, 'listings': listing_type_objects,
                                                  'item_sub_categories': item_sub_categories,
                                                  'services_sub_categories': services_sub_categories,
                                                  'rideshare_sub_categories': rideshare_sub_categories,
                                                  'housing_sub_categories': housing_sub_categories,
                                                  'categories': categories_list, 'subcategory_name': category_type,
                                                  'form_listing_settings': form_listing_settings,
                                                  'category_filter': category_type, 'is_listing': True})


def get_listings_and_remaining(listings):
    count = len(listings)
    if count > 0:
        limit = settings.LISTINGS_PER_PAGE
        query = listings[:limit]
        return query, count - len(query)


def people_listing(request, type_filter=None, item_type=None, template=None, poster=None, recipient=None,
                   extra_context=None, do_filter=False):

    if request.session.get('offset'):
        request.session['offset'] = 0

    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        user_agent_type = 'mobile'
    else:
        user_agent_type = 'desktop'
    endorsement = None
    form = FeedFilterForm(request.GET, request.profile, request.location, item_type,
                          poster, recipient, do_filter)
    trust_form = EndorseForm(instance=endorsement, endorser=None, recipient=None)
    if form.is_valid():
        feed_items, remaining_count, total_items = form.get_results(form.data.get('radio-low'),
                                                                    form.data.get('radio-high'),
                                                                    form.data.get('referral-radio'))
        if do_filter:
            form.update_sticky_filter_prefs()
    else:
        raise Exception(unicode(form.errors))
    if feed_items:
        next_page_date = feed_items[-1].date
    else:
        next_page_date = None
    url_params = request.GET.copy()
    url_params.pop('d', None)
    url_param_str = url_params.urlencode()
    if next_page_date:
        url_params['d'] = next_page_date.strftime(DATE_FORMAT)
    next_page_param_str = url_params.urlencode()

    number_of_pages = len(total_items) / settings.FEED_ITEMS_PER_PAGE

    listing_form = ListingsForms()
    categories_list = Categories.objects.all()
    item_sub_categories = SubCategories.objects.all().filter(categories=1)
    services_sub_categories = SubCategories.objects.all().filter(categories=2)
    rideshare_sub_categories = SubCategories.objects.all().filter(categories=3)
    housing_sub_categories = SubCategories.objects.all().filter(categories=4)
    trust_form = EndorseForm(instance=endorsement, endorser=None, recipient=None)
    payment_form = AcknowledgementForm(max_ripple=None, initial=request.GET)
    contact_form = ContactForm()

    context = locals()
    context.update(extra_context or {})
    return render(request, 'new_templates/people_listing.html',
                  {'url_params': url_params, 'feed_items': feed_items,
                   'next_page_date': next_page_date, 'context': context,
                   'form': form, 'listing_form': listing_form,
                   'poster': poster, 'do_filter': do_filter,
                   'remaining_count': remaining_count,
                   'item_type': item_type,
                   'url_param_str': url_param_str,
                   'next_page_param_str': next_page_param_str,
                   'extra_context': extra_context,
                   'recipient': recipient, 'user_agent_type': user_agent_type,
                   'item_sub_categories': item_sub_categories,
                   'services_sub_categories': services_sub_categories,
                   'rideshare_sub_categories': rideshare_sub_categories,
                   'housing_sub_categories': housing_sub_categories,
                   'categories': categories_list, 'trust_form': trust_form,
                   'payment_form': payment_form, 'contact_form': contact_form,
                   'number_of_pages': number_of_pages})


def parse_products(request, products):
    products_html = ''
    for each_product in products:
        products_html += render_to_string('new_templates/listing_item.html', {'request': request, 'item': each_product})
    return products_html


def product_infinite_scroll(request, offset=settings.LISTING_ITEMS_PER_PAGE):
    offset = int(offset)
    start_session_offset = request.session.get('offset', 0)
    end_session_offset = start_session_offset + offset

    form_listing_settings = FormListingsSettings(request.GET, profile=request.profile, location=request.location,
                                                 start_limit=start_session_offset, end_limit=end_session_offset)
    if form_listing_settings.is_valid():
        listing_items, remaining_count = form_listing_settings.get_results()
    else:
        listing_items = []

    parsed_products = parse_products(request, listing_items)

    if len(listing_items) < offset or not listing_items:
        end_session_offset = 0
    request.session['offset'] = end_session_offset
    return HttpResponse(parsed_products)


def home(request, type_filter=None, item_type=None, template=None, poster=None, recipient=None,
         extra_context=None, do_filter=False):
    """
    url: /home
    """
    if not request.user.is_authenticated():
        return render(request, 'new_templates/home_page.html')

    request.session['offset'] = settings.LISTING_ITEMS_PER_PAGE
    sign_in_form = UserForm
    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        user_agent_type = 'mobile'
    else:
        user_agent_type = 'desktop'
    endorsement = None
    if request.method == 'POST':
        form = ListingsForms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('frontend:home'))
        else:
            print(form.errors)

    people = None
    trusted_only = None
    # GET Request
    form_listing_settings = FormListingsSettings(request.GET, request.profile, request.location, type_filter, do_filter)
    if form_listing_settings.is_valid():
        listing_items, remaining_count = form_listing_settings.get_results()
        next_page_date = listing_items[-1].date if listing_items else None
    else:
        listing_items = remaining_count = next_page_date = None
    url_params = request.GET.copy()
    url_params.pop('d', None)
    if next_page_date:
        url_params['d'] = next_page_date.strftime(DATE_FORMAT)
    next_page_param_str = url_params.urlencode()

    trust_form = EndorseForm(instance=endorsement, endorser=None, recipient=None)
    payment_form = AcknowledgementForm(max_ripple=None, initial=request.GET)
    contact_form = ContactForm()

    form = ListingsForms()
    categories_list = Categories.objects.order_by('id')
    subcategories = SubCategories.objects.all()
    if type_filter in LISTING_TYPE_CHECK:
        # is listing_type filter
        item_type_name = type_filter
    else:
        try:
            item_type_name = SubCategories.objects.filter(id=type_filter).values('sub_categories_text')[0]['sub_categories_text']
        except:
            # is category filter
            item_type_name = type_filter

    item_sub_categories = SubCategories.objects.all().filter(categories=1)
    services_sub_categories = SubCategories.objects.all().filter(categories=2)
    rideshare_sub_categories = SubCategories.objects.all().filter(categories=3)
    housing_sub_categories = SubCategories.objects.all().filter(categories=4)

    return render(request, 'new_templates/product_list.html', {
        'item_sub_categories': item_sub_categories, 'subcategories': subcategories,
        'services_sub_categories': services_sub_categories, 'rideshare_sub_categories': rideshare_sub_categories,
        'housing_sub_categories': housing_sub_categories, 'user_agent_type': user_agent_type,
        'people': people, 'listing_form': form, 'categories': categories_list,
        'trusted_only': trusted_only, 'trust_form': trust_form, 'payment_form': payment_form,
        'contact_form': contact_form, 'form_listing_settings': form_listing_settings,
        'item_type_name': item_type_name, 'is_listing': True, 'url_params': url_params,
        'listing_items': listing_items, 'next_page_date': next_page_date, 'remaining_count': remaining_count,
        'next_page_param_str': next_page_param_str, 'listing_type_filter': type_filter})


def map_visualization(request):

    if request.session.get('offset'):
        request.session['offset'] = 0
    form = ListingsForms()
    item_sub_categories = SubCategories.objects.all().filter(categories=1)
    services_sub_categories = SubCategories.objects.all().filter(categories=2)
    rideshare_sub_categories = SubCategories.objects.all().filter(categories=3)
    housing_sub_categories = SubCategories.objects.all().filter(categories=4)
    payment_form = AcknowledgementForm(max_ripple=None, initial=request.GET)
    categories_list = Categories.objects.all()
    subcategories = SubCategories.objects.all()
    contact_form = ContactForm()

    notification_number = Notification.objects.filter(status='NEW', recipient=request.profile).count()

    return render(request, 'frontend/plugs/map-visualization.html',
                  {'listing_form': form, 'categories': categories_list, 'item_sub_categories': item_sub_categories,
                   'services_sub_categories': services_sub_categories, 'subcategories': subcategories,
                   'rideshare_sub_categories': rideshare_sub_categories,
                   'housing_sub_categories': housing_sub_categories,
                   'payment_form': payment_form, 'contact_form': contact_form,
                   'notification_number': notification_number})


def pre_home(request):
    return render(request, 'home_banner.html')