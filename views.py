# Create your views here.
from Points.models import  Operation_points, History_points, User_points
from django.shortcuts import  render_to_response
from django.http import HttpResponse
from utils.CheckRequestUser import checkRequestUserValidate
from roxedu.settings import logger
import traceback
from django.http import Http404

def current_points(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            user_item = User_points.objects.get(user_id = user)
            points = user_item.points_of_user
            return render_to_response("Points/points_info_base.html", {'user': user, 'points': points})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)


def points_history(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            history_items = History_points.objects.filter(user_id = user)
            return render_to_response("Points/points_history.html", {'user': user, 'history_items': history_items})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)

def get_all_info(request):
    try:
        web_client, user_validate, user = checkRequestUserValidate(request, logger)
        if user:
            user_item = User_points.objects.get(user_id = user)
            points = user_item.points_of_user
            history_items = History_points.objects.filter(user_id = user)
            return render_to_response("Points/points_info.html", {'user': user, 'points': points, 'history_items': history_items})

    except Exception, e:
        msg2 = traceback.format_exc()
        logger.debug(msg2)
        raise Http404



