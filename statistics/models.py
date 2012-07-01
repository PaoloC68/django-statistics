from django.db import models
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from tracking.models import Visitor
from django.db.models.signals import post_init, post_save
from django.contrib.sites.models import Site
from django.conf import settings
import datetime
import logging
try:
    import GeoIP
except Exception, e:
    logging.error("Install python-geoip for tracking GeoIP Data -- %s", e)
    pass


log = logging.getLogger('statistics.models')

untrack_list = ["/favicon","/dajax","/jsi18n","/captcha","/static/","/admin/","/robots.txt/","/sso/"]
untrack = getattr(settings, 'STATISTICS_UNTRACK_URLS', untrack_list)

class Visit(models.Model):
    created    = models.DateTimeField(auto_now_add=True)
    site       = models.CharField(max_length=255)
    url        = models.CharField(max_length=255)
    username   = models.CharField(max_length=255)
    ip_address = models.IPAddressField()
    user_agent = models.CharField(max_length=255)
    geoip_data = models.CharField(max_length=1024, blank=True, null=True)

def log_visit(visitor, stored_fields=['url',
                                      'ip_address', 
                                      'user_agent', 
                                      'geoip_data']):
    data = ((k, getattr(visitor, k)) for k in stored_fields)
    #logging.error("IN LOG VISIT ID: %s -- DIR %s", visitor.id, dir(visitor))
    #logging.error("IN LOG VISIT SESSION_KEY: %s ", visitor.session_key)
    try:
        session = Session.objects.get(session_key=visitor.session_key)
        uid = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=uid).username
    except Exception, e:
        user = "Not Logged User"
    ldata = list(data)
    ldata.append(('site', Site.objects.get_current()))
    ldata.append(('username', user))
    try:
        geoip_file_default = "/usr/share/pyshared/statistics/GeoLiteCity.dat"
        geoip_file = getattr(settings, 'GEO_CITY_LIGHT_FILE', geoip_file_default)
        gi = GeoIP.open(geoip_file,GeoIP.GEOIP_STANDARD)
        ldata.append(('geoip_data', gi.record_by_addr(visitor.ip_address)))
    except Exception, e:
        logging.error(e)
    data = tuple(ldata)
    
    save_to = True
    for i in untrack:
        if getattr(visitor, 'url', '') and getattr(visitor, 'url', '').find(i) > -1:
            #logging.error("Log Visitors: url %s --- %s --- %s", getattr(visitor, 'url', ''), i, getattr(visitor, 'url', '').find(i))
            save_to = False
            break
    #logging.error("SAVE_TO!!! %s", save_to)
    if save_to:
        Visit.objects.create(**dict(data))

def visitor_post_save(sender, **kwargs):
    log_visit(kwargs['instance'])

post_save.connect(visitor_post_save, sender=Visitor)

class DaysPast(models.Model):
    day_number = models.IntegerField('Giorni Passati', max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Giorni Passati'
        verbose_name_plural = 'Giorni Passati'
    
class Months(models.Model):
    nome = models.CharField(max_length=25)
    numero = models.IntegerField(max_length=25)

    class Meta:
        ordering = ["numero"]
        verbose_name = 'Mese'
        verbose_name_plural = 'Mesi'

    def __unicode__(self):
        return self.nome    

class StatisticsMonthYear(models.Model):
    anno = models.IntegerField(max_length=255)
    mese = models.ForeignKey(Months)
    address = models.CharField(max_length=255)
    number = models.IntegerField(max_length=6000)
    
    class Meta:
        ordering = ["anno"]
        verbose_name = 'Statistica Mese e Anno'
        verbose_name_plural = 'Statistiche Mese e Anno'

class StatisticsDates(models.Model):
    year = models.IntegerField(max_length=16)
    month = models.IntegerField(max_length=16)
    day = models.IntegerField(max_length=16)
    address = models.CharField(max_length=255) #site + url
    total_access_year = models.IntegerField(max_length=6000)
    total_access_month = models.IntegerField(max_length=6000)
    total_access_day = models.IntegerField(max_length=6000)

    class Meta:
        ordering = ["address"]
        verbose_name = 'Statistica annuale'
        verbose_name_plural = 'Statistiche annuali'

def log_statistic(visit, stored_fields=[]):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    address = str(visit.site) + visit.url
    if len(StatisticsDates.objects.filter(year=int(year), address=address)) == 0:
        logging.error("nuovo anno o nuovo indirizzo, creo tutto nuovo da 1")
        newstatistics = StatisticsDates()
        newstatistics.year = year
        newstatistics.month = month
        newstatistics.day = day
        newstatistics.address = address
        newstatistics.total_access_year = 1
        newstatistics.total_access_month = 1
        newstatistics.total_access_day = 1
        newstatistics.save()
        #FOR STATISTICS MONTH YEAR
        newstat = StatisticsMonthYear()
        newstat.anno = year
        newstat.mese, created = Months.objects.get_or_create(numero=int(month),nome=datetime.datetime.now().strftime('%B'))
        newstat.address = address
        newstat.number = 1
        newstat.save()
        #Visit.objects.get(id=visit.id).delete()
        return
    if len(StatisticsDates.objects.filter(year=int(year), month=int(month), day=int(day), address=address)) > 0:
        #logging.error("Tutto gia presente, aumento il conto totale")
        statistic = StatisticsDates.objects.get(year=int(year), month=int(month), day=int(day), address=address)
        statistic.total_access_year += 1
        statistic.total_access_month += 1
        statistic.total_access_day += 1
        statistic.save()
        #FOR STATISTICS MONTH YEAR
        mese, created = Months.objects.get_or_create(numero=int(month),nome=datetime.datetime.now().strftime('%B'))
        try:
            stat = StatisticsMonthYear.objects.get(address=address, anno=year, mese=mese)
            stat.number += 1
            stat.save()
            #logging.error("StatisticsMonthYear Esistente")
        except:
            stat = StatisticsMonthYear(address=address, anno=year, mese=mese, number=1)
            stat.save()
            #logging.error("StatisticsMonthYear non Esistente, ricreato")
        #Visit.objects.get(id=visit.id).delete()
        return
    else:
        #logging.error("qualcosa di nuovo, da ragionare a fondo")
        stat_day = StatisticsDates.objects.get(address=address, year=int(year))
        # se nuovo mese, cambio il giorno e il mese ed azzero il day, il month ma non year e total
        if stat_day.month != month:
            #logging.error("nuovo mese")
	    stat_day.month = month
            stat_day.total_access_day = 1
            stat_day.total_access_month = 1
            stat_day.total_access_year += 1
            stat_day.save()
            #logging.error("nuovo mese StatisticDates %s", stat_day)
            #FOR STATISTICS MONTH YEAR New Month
            stat = StatisticsMonthYear()
            stat.anno = int(year)
            stat.mese, created = Months.objects.get_or_create(numero=int(month),nome=datetime.datetime.now().strftime('%B'))
            stat.address = address
            stat.number = 1
            stat.save()
            #logging.error("nuovo mese Statisticmonthyear %s", stat)
            #Visit.objects.get(id=visit.id).delete()
            return
        # se nuovo giorno, cambio il giorno e azzero il conto del day ma non quello di month, year e total
        if stat_day.day != day:
            #logging.error("nuovo giorno")
            stat_day.day = day
            stat_day.total_access_day = 1
            stat_day.total_access_month += 1
            stat_day.total_access_year += 1
            stat_day.save()
            mese, created = Months.objects.get_or_create(numero=int(month),nome=datetime.datetime.now().strftime('%B'))
            stat = StatisticsMonthYear.objects.get(address=address, anno=year, mese=mese)
            stat.number += 1
            stat.save()
            #Visit.objects.get(id=visit.id).delete()
            return


def visit_post_save(sender, **kwargs):
    log_statistic(kwargs['instance'])
    

post_save.connect(visit_post_save, sender=Visit)

