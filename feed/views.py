# from general.util import render
from django.shortcuts import render
from geo.util import location_required
from feed.forms import FeedFilterForm, DATE_FORMAT
from django.views.decorators.cache import cache_page
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME


def feed(request, item_type=None, template='feed.html', poster=None,
         recipient=None, extra_context=None, do_filter=False):
    """
    Generic view for displaying feed items.

    Set do_filter=True to process with radius and trusted filters.
    """
    if not request.location:
        return HttpResponseRedirect("%s?%s=%s" % (
            reverse('locator'), REDIRECT_FIELD_NAME, request.path))
    else:
        form = FeedFilterForm(
            request.GET, request.profile, request.location, item_type,
            poster, recipient, do_filter)
        if form.is_valid():
            feed_items, remaining_count = form.get_results()
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

        context = locals()
        context.update(extra_context or {})
        return render(request, 'feed.html', {'url_params': url_params, 'feed_items': feed_items,
                                             'next_page_date': next_page_date, 'context': context, 'form': form,
                                             'poster': poster, 'do_filter': do_filter, 'remaining_count': remaining_count,
                                             'item_type': item_type, 'template': template, 'url_param_str': url_param_str,
                                             'next_page_param_str': next_page_param_str, 'extra_content': extra_context,
                                             'recipient': recipient})
