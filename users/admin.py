from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User, UserPreference, UserWatched, UserWatchlist


class UserAdmin(DefaultUserAdmin):
    list_display = ["username", "is_staff"]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ["date_of_birth"]}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


class UserStatsAdmin(admin.ModelAdmin):
    list_display = ["user", "num_films", "updated_at"]

    @admin.display(description="# Films")
    def num_films(self, obj):
        return obj.num_films


class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "pick_order_criteria"]


admin.site.register(User, UserAdmin)
admin.site.register(UserPreference, UserPreferenceAdmin)
admin.site.register(UserWatched, UserStatsAdmin)
admin.site.register(UserWatchlist, UserStatsAdmin)
