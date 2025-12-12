from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from urllib import request as urlrequest, parse as urlparse
import json


def home_page(request):
    api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
    return render(request, 'home.html', {'OPENWEATHER_API_KEY': api_key})


def about_page(request):
    return render(request, 'about.html')


def contact_page(request):
    return render(request, 'contact.html')


def weather_api(request):
    """Proxy endpoint: /api/weather/?q=<city>
    Calls OpenWeather API server-side using `OPENWEATHER_API_KEY` from settings
    and returns the JSON response (passes through status codes).
    """
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'message': 'Missing query parameter `q`.'}, status=400)

    api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
    if not api_key:
        return JsonResponse({'message': 'Server: OPENWEATHER_API_KEY not configured.'}, status=500)

    params = urlparse.urlencode({'q': q, 'appid': api_key, 'units': 'metric'})
    url = f'https://api.openweathermap.org/data/2.5/weather?{params}'
    print(f"DEBUG: Calling OpenWeather URL: {url}")  # Debug log

    try:
        with urlrequest.urlopen(url, timeout=10) as resp:
            raw = resp.read()
            data = json.loads(raw.decode('utf-8'))
            status_code = resp.getcode()
            print(f"DEBUG: OpenWeather response status: {status_code}, data: {data}")  # Debug log
    except urlrequest.HTTPError as e:
        try:
            body = e.read().decode('utf-8')
            data = json.loads(body)
        except Exception:
            data = {'message': str(e)}
        print(f"DEBUG: OpenWeather HTTPError: {e.code}, data: {data}")  # Debug log
        return JsonResponse(data, status=e.code)
    except Exception as e:
        print(f"DEBUG: Network error: {e}")  # Debug log
        return JsonResponse({'message': f'Network error: {e}'}, status=502)

    return JsonResponse(data, status=status_code)
