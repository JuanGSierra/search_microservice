from django.urls import path
from django.conf.urls import url
from app_search_microservice import views 
 
urlpatterns = [ 
    path('routes/', views.get_all_routes),
    path('routes/<int:routeID>', views.get_route),
    path('bus_stop/', views.get_all_bus_stop),
    path('bus_stop/<int:routeID>', views.get_bus_stops_for_routeID),
		path('bus_stop/detailed/<clientInput>', views.get_stop_by_cenefa_or_name_or_direccion),
		path('bus_stop/by_id/<clientInput>', views.get_stop_by_cenefa),
    path('routes/detailed/<clientInput>', views.get_route_by_denomination_or_name),
    url(r'^routes/buses_transited/$', views.get_buses_transited)
]