__author__ = 'shuaili'

from django.conf.urls import patterns, include, url

urlpatterns = patterns('Points.views',
# Examples:
# url(r'^$', 'Dropbox.views.home', name='home'),
# url(r'^Dropbox/', include('Dropbox.foo.urls')),

# Uncomment the admin/doc line below to enable admin documentation:
# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

# Uncomment the next line to enable the admin:
# url(r'^admin/', include(admin.site.urls)),
url(r'bonus_info', "get_all_info"),
url(r'bonus_history', "get_all_info"),
url(r'bonus_rule', "get_bonus_rule"),
url(r'bonus_record/$', "get_some_bonus_record"),
url(r'bonus_all_record/$', "get_all_bonus_record"),
url(r'bonus_all_record/(\d+)/$', "get_bonus_record"),
url(r'bonus_record_page/$', "bonus_record"),
)