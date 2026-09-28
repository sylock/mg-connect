from django.urls import path

from achievements import views

app_name = "achievements"

urlpatterns = [
    path("", views.achievement_list, name="list"),
    path("new/", views.achievement_create, name="create"),
    path("<uuid:pk>/", views.achievement_detail, name="detail"),
    path("<uuid:pk>/approve/", views.achievement_approve, name="approve"),
    path("<uuid:pk>/reject/", views.achievement_reject, name="reject"),
    path("<uuid:pk>/void/", views.achievement_void, name="void"),
    path("<uuid:pk>/correct/", views.achievement_correct, name="correct"),
]
