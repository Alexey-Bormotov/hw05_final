import datetime as dt


def year(request):
    year = dt.date.today().year
    return {
        'year': year
    }
