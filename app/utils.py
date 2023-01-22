import datetime

def uuid1_time_to_datetime(time: int):
    """
    Start datetime is on October 15th, 1582.
    Why? -> https://en.wikipedia.org/wiki/1582

    adding this datetime to uuid.uuid1.time(),
    divided by 10 (ignoreing the remainder //)
    """

    return datetime.datetime(1582, 10, 15) + datetime.timedelta(microseconds=time//10)