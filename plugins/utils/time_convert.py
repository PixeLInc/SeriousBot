import datetime

def convert_time(to_date, hlist = None):
    today = datetime.datetime.now()
    ndate = (today + to_date)
    if hlist is not None:
        ndate = ndate.replace(hour=hlist[0], minute=hlist[1], second=hlist[2])

    delta = ndate - today

    days, seconds = delta.days, delta.seconds
    hours = int(days / 24 + seconds // 3600)
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return {'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}

def get_next_friday():
    friday = convert_time(datetime.timedelta((4 - datetime.datetime.now().weekday()) % 7), [21, 0, 0])

    if friday.get('days', 0) == -1:
        return 'The time has come. It is already done.'

    return '{} day{}, {} hour{}, {} minute{}, {} second{}'.format(
        friday.get('days', 0),
        's' if friday.get('days', -1) != 1 else '',
        friday.get('hours', 0),
        's' if friday.get('hours', -1) != 1 else '',
        friday.get('minutes', 0),
        's' if friday.get('minutes', -1) != 1 else '',
        friday.get('seconds', 0),
        's' if friday.get('seconds', -1) != 1 else '',
        )

