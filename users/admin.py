from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User, UserWatched, UserWatchlist


class UserAdmin(DefaultUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "date_of_birth", "email")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


class UserStatsAdmin(admin.ModelAdmin):
    list_display = ["user", "num_films", "updated_at"]

    def num_films(self, obj):
        return obj.num_films

    num_films.short_description = "# Films"


admin.site.register(User, UserAdmin)
admin.site.register(UserWatched, UserStatsAdmin)
admin.site.register(UserWatchlist, UserStatsAdmin)
