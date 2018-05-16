from profile.models import Profile


class ProfileMiddleware(object):
    def process_request(self, request):
        "Populate request with user profile, for convenience."
        request.profile = None
        if request.user.is_authenticated():
            try:
                request.profile = Profile.objects.select_related('user').prefetch_related('trusted_profiles')\
                    .get(user=request.user)
            except Profile.DoesNotExist:
                pass
