from django.shortcuts import render

def error_404(request, exception):
    """Обработчик страницы 404 (страница не найдена)"""
    return render(request, '404.html', status=404)

def error_500(request):
    """Обработчик страницы 500 (ошибка сервера)"""
    return render(request, '500.html', status=500) 