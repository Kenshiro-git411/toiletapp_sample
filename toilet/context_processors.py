def common(request):
    station_id = request.session.get('search_station_id')
    
    context = {
        "site_name": "トイレGo",
        "common_station_id": station_id,
        
    }
    return context