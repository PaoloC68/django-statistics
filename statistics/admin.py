from django.db import models
from django.core.cache import cache
from django.contrib import admin
from statistics.models import *
from django.contrib.admin.widgets import AdminDateWidget
from django.http import HttpResponse
from datetime import datetime, timedelta, date
import csv

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            writer.writerow(list(field_names))
        for obj in queryset:
            writer.writerow([unicode(getattr(obj, field)).encode("utf-8","replace") for field in field_names])
        return response
    export_as_csv.short_description = description
    return export_as_csv

def clean_all_past_visits(self, request, queryset):
    try:
        days = DaysPast.objects.all()[0].day_number #per forza il primo elemento
        date_limit = date.today() - timedelta(days=days)
        olds = Visit.objects.filter(created__lt=date_limit)
        length = len(olds)
        olds.delete()
        self.message_user(request, "Eliminati %s vecchie Visits" % length)
    except:
        days = None
        self.message_user(request, "Campo Giorni Passati Nullo")
        pass

clean_all_past_visits.short_description = "Pulisce Visits piu' vecchie di n giorni passati"

def clean_all_not_logged_users(self, request, queryset):
    not_logged = Visit.objects.filter(username="Not Logged User")
    length = len(not_logged)
    #logging.error("in cleaning not logged %s", len(not_logged))
    not_logged.delete()
    self.message_user(request, "Eliminati %s Not Logged Users" % length)
clean_all_not_logged_users.short_description = "Clean all Not logged User Visits"

class VisitAdmin(admin.ModelAdmin):
    list_display = ['site', 'url', 'username', 'ip_address', 'user_agent', 'geoip_data', 'created']
    list_filter = ('username', 'created','site')
    search_fields = ['site', 'url', 'username', 'ip_address', 'user_agent']
    actions = [clean_all_not_logged_users,clean_all_past_visits,export_as_csv_action("CSV Export", fields=['site','url','username','ip_address','created'])]

class StatisticsDatesAdmin(admin.ModelAdmin):
    list_display = ['address','total_access_day','total_access_month','total_access_year','year']
    actions = [export_as_csv_action("CSV Export", fields=['address','total_access_year'])]

class StatisticsMonthYearInline(admin.TabularInline):
    model = StatisticsMonthYear

class StatisticsMonthYearAdmin(admin.ModelAdmin):
    list_display = ['anno','mese','address','number']
    search_fields = ['address','mese']
    list_filter = ('mese',)
    actions = [export_as_csv_action("CSV Export", fields=['anno','mese','address','number'])]

class MonthsAdmin(admin.ModelAdmin):
    list_display = ['nome','numero']
    inlines = [StatisticsMonthYearInline]

class DaysPastAdmin(admin.ModelAdmin):
    list_display = ['id','day_number']
    list_editable = ('day_number',)

admin.site.register(Visit, VisitAdmin)
admin.site.register(StatisticsDates, StatisticsDatesAdmin)
admin.site.register(StatisticsMonthYear, StatisticsMonthYearAdmin)
admin.site.register(Months, MonthsAdmin)
admin.site.register(DaysPast, DaysPastAdmin)

