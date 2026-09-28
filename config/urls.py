from django.contrib import admin
from django.urls import include, path

from accounts import views as account_views
from achievements.views import evidence_download

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("", account_views.home, name="home"),
    path("agenda/", account_views.agenda_placeholder, name="agenda"),
    path("reports/", account_views.reports_placeholder, name="reports"),
    path("achievements/", include("achievements.urls")),
    path("evidence/<uuid:pk>/", evidence_download, name="evidence"),
    path(
        "leave/",
        account_views.feature_coming_soon,
        {"feature": "leave"},
        name="leave",
    ),
    path(
        "attendance/clock/",
        account_views.feature_coming_soon,
        {"feature": "clock"},
        name="clock",
    ),
]
