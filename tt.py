import datetime

s = "/img/temp/Rhi8wd9IDkzd5696abf78b8c433c773e508fd82e2619.jpg"
a = s.split("/img/")[1]
print(a)


def utc_to_local(utc):
    # utc = "2018-07-17T08:48:31.151Z"
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    utcTime = datetime.datetime.strptime(utc, UTC_FORMAT)
    localtime = utcTime + datetime.timedelta(hours=8)
    localtime = datetime.datetime.strftime(localtime, '%Y-%m-%d %H:%M:%S')
    return localtime


print(utc_to_local("2022-01-11T02:04:51.117639Z"))
