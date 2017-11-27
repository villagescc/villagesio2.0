from django.contrib import admin

from profile.models import Profile, Settings


class SettingsInline(admin.StackedInline):
    model = Settings


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'location',
        'created',
        'updated',
        'last_login',
    )

    search_fields = ('user__username', 'name')

    ordering = ('-user__last_login',)

    inlines = (SettingsInline,)

    def last_login(self, profile):
        return profile.user.last_login


admin.site.register(Profile, ProfileAdmin)
