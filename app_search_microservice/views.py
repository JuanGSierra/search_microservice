import firebase_admin
import re
from firebase_admin import credentials
from firebase_admin import firestore

from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view
from datetime import datetime, time

cred = credentials.Certificate('ruteamearchi-firebase.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


@api_view(['GET'])
def get_all_routes(request):
    try:
        result = db.collection(u'routes').stream()
        list_result = []
        for route in result:
            list_result.append(route.to_dict())
        return JsonResponse(list_result, safe=False)

    except Exception as e:
        return JsonResponse({'mesage': f'Error: {e}'})


@api_view(['GET'])
def get_route(request, routeID):
    try:
        result = db.collection(u'routes').document(f'{routeID}').get()
        return JsonResponse(result.to_dict(), safe=False)

    except Exception as e:
        return JsonResponse({'mesage': f'Error: {e}'})


@api_view(['GET'])
def get_route_by_denomination_or_name(request, clientInput):
    try:
        routes = db.collection(u'routes').document(u'ids').get()
        routes = routes.to_dict()
        list_return = []
        for route in routes:
            if (re.search(f'{clientInput}', routes[route]['denomination'], flags=re.M | re.I) or re.search(f'{clientInput}', routes[route]['name'], flags=re.M | re.I)):
                list_return.append(route)
        return JsonResponse(list_return, safe=False)
    except Exception as e:
        return JsonResponse({'mesage': f'Error: {e}'})

@api_view(['GET'])
def get_buses_transited(request):
    try:
        print(request.GET["routeID"],request.GET["initialDate"],request.GET["finalDate"])
        routeID = request.GET["routeID"]
        input_initialDate = request.GET["initialDate"]
        input_finalDate = request.GET["finalDate"]
        initialDate = datetime.fromisoformat(input_initialDate)
        finalDate = datetime.fromisoformat(input_finalDate)
        raw_route = db.collection(u'routes').document(  f'{routeID}').get()
        route = raw_route.to_dict()

        periodicity = route['schedule']['periodicity']
        startHour = route['schedule']['startHour']
        endHour = route['schedule']['endHour']

        workableHoursPerDay = endHour - startHour
        totalOfBuses = 0
        hoursLeftToWorkInitialDate = datetime.combine(datetime.today(),time(endHour,0)) - datetime.combine(datetime.today(),initialDate.time())
        substractDates = finalDate - initialDate
        totalHoursLeft = substractDates.total_seconds()/60/60
        if(substractDates.total_seconds()/60/60 <= hoursLeftToWorkInitialDate.total_seconds()/60/60):
          totalOfBuses = substractDates.total_seconds()/60 //periodicity
          return JsonResponse(totalOfBuses,safe=False)
        totalOfBuses = hoursLeftToWorkInitialDate.total_seconds()/60//periodicity
        totalHoursLeft -= hoursLeftToWorkInitialDate.total_seconds()/60/60
        totalHoursLeft -= 24 - endHour + startHour
        while(totalHoursLeft>0):
          if(totalHoursLeft <= workableHoursPerDay):
            totalOfBuses += totalHoursLeft*60//periodicity
            totalHoursLeft=0
            print(totalHoursLeft,workableHoursPerDay)
          else:
            totalOfBuses += workableHoursPerDay*60//periodicity
            totalHoursLeft -= workableHoursPerDay
          totalHoursLeft -= 24 - endHour + startHour
        return JsonResponse(totalOfBuses,safe=False)
    except Exception as e:
        return JsonResponse({'message': f'Error: {e}'})


@api_view(['GET'])
def get_all_bus_stop(request):
    try:
        result = db.collection(u'stops').stream()
        list_result = []
        for stop in result:
            list_result.append(stop.to_dict())
        return JsonResponse(list_result, safe=False)
    except Exception as e:
        return JsonResponse({'mesage': f'Error: {e}'})

@api_view(['GET'])
def get_stop_by_cenefa(request, clientInput):
    try:
        result = db.collection(u'stops').document(f'{clientInput}').get()
        return JsonResponse(result.to_dict(), safe=False)
    except Exception as e:
        return JsonResponse({'mesage': f'Error: {e}'})

@api_view(['GET'])
def get_bus_stops_for_routeID(request, routeID):
    try:
        route_result = db.collection(u'routes').document(f'{routeID}').get()
        codigo_definitivo_ruta_zonal = route_result.to_dict(
        )['properties']['codigo_definitivo_ruta_zonal']
        result = db.collection(u'stops').where(
            'ruta_comercial', 'array_contains', f'{codigo_definitivo_ruta_zonal}').get()
        list_result = []
        for stop in result:
            list_result.append(stop.to_dict())
        return JsonResponse(list_result, safe=False)
    except Exception as e:
        return JsonResponse({'mesage': f'Error: {e}'})

@api_view(['GET'])
def get_stop_by_cenefa_or_name_or_direccion(request, clientInput):
    try:
        stop_list = []
        print(clientInput)
        for i in range(0,7):
            stops = db.collection(u'stops').document(f'index_with_data_{i}').get()
            stops = stops.to_dict()
            for stop in stops:
                if (re.search(f'{clientInput}', stops[stop]['cenefa_paradero'], flags=re.M | re.I) or re.search(f'{clientInput}', stops[stop]['direccion_paradero'] if 'direccion_paradero' in stops[stop].keys() else "", flags=re.M | re.I) or re.search(f'{clientInput}', stops[stop]['nombre_paradero'] if 'nombre_paradero' in stops[stop].keys() else "", flags=re.M | re.I)):
                    stop_list.append(stops[stop])
        return JsonResponse(stop_list, safe=False)
    except Exception as e:
        return JsonResponse({'mesage': f'Error: {e}'})

