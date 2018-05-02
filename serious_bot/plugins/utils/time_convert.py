import datetime


def next_weekday(d, weekday, time):
    """
        Weekday: 0 - Monday, 1 - Tuesday, 2 - Wednsday, 3 - Thursday, 4 - Friday, 5 - Saturday, 6 - Sunday
    """
    d = d - datetime.timedelta(hours=6)
    dr = d.replace(hour=time[0], minute=time[1], second=time[2])
    delta = dr - d

    hours, minutes, seconds = (delta.seconds // 3600, (delta.seconds // 60) % 60, (delta.seconds) % 60)

    days_ahead = weekday - d.weekday()
    if days_ahead < 0 or (delta.days < 0 or (hours >= time[0] and minutes >= time[1] and seconds >= time[2])):
        # It's for sure past the day, let's move on.
        days_ahead += 6

    return {
        'delta': delta,
        'time_data': [days_ahead, hours, minutes, seconds],
        'next_date': (dr + datetime.timedelta(days_ahead))
    }


def get_next_friday():
    next_data = next_weekday(datetime.datetime.utcnow(), 4, [21, 0, 0])
    time_data = next_data['time_data']

    if len(time_data) < 4:
        return 'Error getting time!'

    return '{} day{}, {} hour{}, {} minute{}, {} second{}'.format(
        time_data[0],
        's' if time_data[0] != 1 else '',  # THIS
        time_data[1],
        's' if time_data[1] != 1 else '',  # IS
        time_data[2],
        's' if time_data[2] != 1 else '',  # A
        time_data[3],
        's' if time_data[3] != 1 else ''  # MEME
    )
