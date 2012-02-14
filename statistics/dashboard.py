from grappelli.dashboard import modules

class StatisticsModule(modules.DashboardModule):
    template = 'statistics/fragments/dashboard_module.html'
    show_title = False
