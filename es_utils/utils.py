from django.conf import settings


def handle_document(listing_obj):

    es_doc = {
        'listing_id': listing_obj.id,
        'listing_title': listing_obj.title,
        'price': listing_obj.price,
        'listing_type': listing_obj.listing_type,
        'user_id': listing_obj.user.id,
        'user_name': listing_obj.user.username,
        'category': listing_obj.subcategories.categories.categories_text,
        'subcategory': listing_obj.subcategories.sub_categories_text,
        'description': listing_obj.description,
        'created': listing_obj.created,
        'updated': listing_obj.updated,
        'location': {
            'lat': int(listing_obj.user.profile.location.point.coords[0]),
            'lon': int(listing_obj.user.profile.location.point.coords[1]),
        },
        'listing_url': 'http://www.villages.io/listing_details/{0}'.format(listing_obj.id)
    }
    if 'location' in es_doc:
        del es_doc['location']

    if listing_obj.user.profile.location:
        city = listing_obj.user.profile.location.city
        state = listing_obj.user.profile.location.state
        country = listing_obj.user.profile.location.country
        lat = listing_obj.user.profile.location.point.coords[0]
        lon = listing_obj.user.profile.location.point.coords[1]
        location_full_name = listing_obj.user.profile.location.full_name()
        es_doc['location'] = {
            'lat': float(lon),
            'lon': float(lat)
        }
        es_doc['city'] = city
        es_doc['state'] = state
        es_doc['country'] = country
        es_doc['location_full_name'] = location_full_name
    return es_doc


def save_document(listing_obj):
    document = handle_document(listing_obj)
    settings.ELASTICSEARCH.index(index="villages", doc_type="listings", body=document)

