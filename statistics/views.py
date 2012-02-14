from datetime import timedelta

from django.shortcuts import render_to_response
# Create your views here.
from statistics.models import Visit


def recent_graph(request, 
                 since=None, 
                 time_grid=timedelta(0,0,0,0,1),
                 grid_x_step=10,
                 graph_scale = float(1)/3):
    visits = Visit.objects.all()
    if since:
        visits.filter(created__gte=since)
    visits.order_by('-created')
    max_height = 0
    if visits.exists():
        graph_duration = visits.latest('created').created - visits[0].created
        visits_aggregated = []
        step = []
        start_time = step_time = visits[0].created
        step_delta = step_time + time_grid
        for visit in visits:
            if visit.created <= step_delta:
                step += visit,
            else:
                if len(step) > max_height:
                    max_height = len(step)
                visits_aggregated += [step, 
                                    ((visit.created - \
                                        start_time).seconds/time_grid.seconds)*grid_x_step],
                step = [visit,]
                step_time = visit.created
                step_delta = step_time + time_grid

    else:
        graph_duration = timedelta(0)
        visits_aggregated = []
    graph_steps = graph_duration.seconds/time_grid.seconds
    width = graph_steps*grid_x_step
    height = int(width*graph_scale)
    y_step = height/(max_height+1)
    for step in visits_aggregated:
        step += len(step[0])*y_step,
    context = {'width':width,
               'height':height,
               'steps':visits_aggregated}
    return render_to_response('statistics/stats.svg', context, mimetype='image/svg+xml')