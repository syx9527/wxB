from django.utils import timezone

a = "533122199812101414"
b = a[6:10] + '-' + a[10:12] + '-' + a[12:14]
print(b)
da = timezone.datetime.strptime(
    a[6:14], '%Y%m%d')
print(da)
