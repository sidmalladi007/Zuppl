from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/signup/$', views.sign_up, name='signup'),
    url(r'^accounts/create-account/$', views.create_account, name='create-account'),
    url(r'^accounts/login/$', views.sign_in, name='login'),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    url(r'^my-events/$', views.my_events, name='my-events'),
    url(r'^attending-events/$', views.attending_events, name='attending-events'),
    url(r'^trends/$', views.trending_zuppls, name='trends'),
    url(r'^recent/$', views.recent_zuppls, name='recent'),
    url(r'^soon/$', views.soon_zuppls, name='soon'),
    url(r'^accounts/logout/$', views.sign_out, name='logout'),
    url(r'^create-zuppl/$', views.create_page, name='create'),
    url(r'^zuppl-success/$', views.add_zuppl, name='add-zuppl'),
    url(r'^(?P<event_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<event_id>[0-9]+)/edit/$', views.edit_page, name='edit-page'),
    url(r'^(?P<event_id>[0-9]+)/edit-success/$', views.edit_zuppl, name='edit-zuppl'),
    url(r'^(?P<event_id>[0-9]+)/delete/$', views.delete_zuppl, name='delete-event'),
    url(r'^(?P<event_id>[0-9]+)/attend/$', views.attend, name='attend'),
    url(r'^(?P<event_id>[0-9]+)/leave/$', views.leave, name='leave'),
    url(r'^(?P<event_id>[0-9]+)/comment/$', views.add_comment, name='comment'),
    url(r'^(?P<comment_id>[0-9]+)/delete-comment/$', views.delete_comment, name='delete-comment'),
]