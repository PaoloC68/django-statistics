from datetime import datetime, timedelta, date
from django import template
from django.template.defaultfilters import stringfilter
from statistics.models import *
import logging

register = template.Library()


class VisitHistory(template.Node):
    def __init__(self, var_name):
        self.varname = var_name

    def render(self, context):
        try:
            total = Visit.objects.all()
        except Exception, e:
            logging.error(e)
            total = []
        context[self.varname] = total
        return ''

@register.tag
def get_visit_history(parser, token):
    "Return all visits"
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]
    #print "Tag: %s -- Var: %s -- User: %s" % (tag_name, var_name, user_name)
    return VisitHistory(var_name)

# USAGE
# {% get_visit_history total %}
# {{ total }}  -> return total visit


class VisitHistorySum(template.Node):
    def __init__(self, var_name):
        self.varname = var_name

    def render(self, context):
        try:
            year = datetime.datetime.now().year
            results = StatisticsMonthYear.objects.filter(anno=year)
            #mesi = Months.objects.all()
            Gennaio = 0
            Febbraio = 0
            Marzo = 0
            Aprile = 0
            Maggio = 0
            Giugno = 0
            Luglio = 0
            Agosto = 0
            Settembre = 0
            Ottobre = 0
            Novembre = 0
            Dicembre = 0
            for i in results:
                if i.mese.nome == "Gennaio": Gennaio += i.number
                if i.mese.nome == "Febbraio": Febbraio += i.number
                if i.mese.nome == "Marzo": Marzo += i.number
                if i.mese.nome == "Aprile": Aprile += i.number
                if i.mese.nome == "Maggio": Maggio += i.number
                if i.mese.nome == "Giugno": Giugno += i.number
                if i.mese.nome == "Luglio": Luglio += i.number
                if i.mese.nome == "Agosto": Agosto += i.number
                if i.mese.nome == "Settembre": Settembre += i.number
                if i.mese.nome == "Ottobre": Ottobre += i.number
                if i.mese.nome == "Novembre": Novembre += i.number
                if i.mese.nome == "Dicembre": Dicembre += i.number
            #logging.error("MESI %s %s %s %s %s %s %s %s %s", Gennaio, Febbraio, Marzo, Aprile, Maggio, Giugno, Luglio, Agosto, Settembre)
            results = [("Gennaio", Gennaio),("Febbraio", Febbraio),("Marzo", Marzo),("Aprile", Aprile),("Maggio", Maggio),("Giugno", Giugno),("Luglio", Luglio),("Agosto", Agosto),("Settembre", Settembre),("Ottobre", Ottobre),("Novembre", Novembre),("Dicembre", Dicembre)]
            #logging.error(results)
        except Exception, e:
            logging.error(e)
            results = []
        #logging.error("RES %s",results)
        context[self.varname] = results
        return ''

@register.tag
def get_visit_history_sum(parser, token):
    "Return all visits"
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires one argument" % token.contents.split()[0]
    #print "Tag: %s -- Var: %s -- User: %s" % (tag_name, var_name, user_name)
    return VisitHistorySum(var_name)

# USAGE
# {% get_visit_history_sum total %}
# {{ total }}  -> return total sum visit in graph

