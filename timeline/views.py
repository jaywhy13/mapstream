from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from BTrees.OOBTree import OOBTree
from stream.models import *
import datetime
import json

MAXDAYS = 31
MAXMONTHS = 12
MAXYEARS = 5
MAXWEEKS = 52

def add_event(tree, event):
    date = event.occurred_at
    if not date:
        return tree

    date_str = date.strftime("%Y-%m-%W")
    values = []
    
    id = event.pk
    caption = event.name
    ymwd = date.strftime("%Y-%m-%W-%d")
    
    if tree.has_key(date_str):
        values = tree[date_str]

    values.append(dict(id=id, caption=caption, ymwd=ymwd))
    tree[date_str] = values

    return tree

def get_event_tree(use_cache=True):
    t = OOBTree()
    events = Event.objects.all()
    for event in events:
        add_event(t, event)
    return t

def get_events(year=None, month=None, week=None, years=None, months=None, weeks=None, days=None):

    t = get_event_tree()

    if not len(t): # if we get an empty tree return a blank list
        return []
    
    if not year:
        try:
            year = int(t.minKey().split("-")[0]) 
        except Exception:
            year = datetime.datetime.now().year
        
    if not month:
        try:
            month = int(t.minKey().split("-")[1]) 
        except Exception:
            month = 1

    if not week:
        try:
            week = int(t.minKey().split("-")[2]) 
        except Exception:
            week = 1

    # pad the month and week
    if month < 10:
        month = '0%s' % month

    if week < 10:
        week = '0%s' % week

    start_date_str = "%s-%s-%s" % (year, month, week)
    
    # if we don't set the week day, everything goes wrong
    start_date = datetime.datetime.strptime(start_date_str + "-1", "%Y-%m-%W-%w")
    
    # set up parameters to set the stop date
    if not years:
        years = 0 # use a default of 1000 years into the future
    else:
        years = int(years)

    if not months:
        months = 0
    else:
        months = int(months)

    if not weeks:
        weeks = 0
    else:
        weeks = int(weeks)

    if not days:
        days = 0
    else:
        days = int(days)

    days = days + years * 356 + months * 31

    print "Will start at %s" % (start_date.strftime("%Y-%m-%d") )

    if years > 0 or months > 0 or weeks > 0 or days > 0:
        date_add = datetime.timedelta(days=days, weeks=weeks)
        end_date = start_date + date_add
        end_date_str = end_date.strftime("%Y-%m-%W")
        print "Will end at %s" % end_date.strftime("%Y-%m-%d")
        results = list(t.values(min=start_date_str, max=end_date_str))
    else:
        results = list(t.values(min=start_date_str))

    all_results = []
    for result in results:
        all_results.extend(result)

    return all_results

def filter_events_from_request(request, year=None, month=None, week=None):
    params = request.GET

    # grab some filter parameters from the request
    days = params.get('days', None)
    weeks = params.get('weeks', None)
    months = params.get('months', None)
    years = params.get('years', None)

    try:
        if days:
            days = min(int(days), MAXDAYS)
    except Exception as e:
        days = None

    try:
        if weeks:
            weeks = min(int(weeks), MAXWEEKS)
    except Exception as e:
        weeks = None

    try:
        if months:
            months = min(int(months),MAXMONTHS)
    except Exception:
        months = None

    try:
        if years:
            years = min(int(years), MAXYEARS)
    except Exception:
        years = None

    results = get_events(year=year, month=month, week=week, years=years, months=months, weeks=weeks, days=days)

    return results

def group(request, mode="month", year=None, month=None, week=None, aggregate=False):

    print "Mode: %s" % mode

    if request.method == 'GET':
        params = request.GET
    else:
        raise Http404

    # check the mode
    if mode not in ["year", "month", "week", "day"]:
        raise Http404

    results = filter_events_from_request(request, year=year, month=month, week=week)
    grouped_results = {}
    total = len(results)
    mode = str(mode)
    for result in results:
        ymwd = result["ymwd"]
        year, month, week, day = ymwd.split("-")
        
        if mode == "year":
            prefix = year
        elif mode == "month":
            prefix = "%s-%s" % (year, month)
        elif mode == "week":
            prefix = "%s-%s-%s" % (year, month, week)
        elif mode == "day":
            prefix = ymwd
            
        if aggregate:
            prefix_results = grouped_results.get(prefix,0)
            prefix_results += len([result])
            grouped_results[prefix] = prefix_results
        else:
            prefix_results = grouped_results.get(prefix,[])
            prefix_results.extend([result])
            grouped_results[prefix] = prefix_results
    
    resp = json.dumps(dict(results=grouped_results, total=total))
    return HttpResponse(resp)
    
    
    
def time(request, year=None, month=None, week=None):

    if request.method == 'GET':
        params = request.GET
    else:
        raise Http404

    results = filter_events_from_request(request, year=year, month=month, week=week)
    total = len(results)
    resp = json.dumps(dict(results=results, total=total))

    return HttpResponse(resp)

