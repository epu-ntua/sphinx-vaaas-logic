import datetime

time = datetime.datetime.now()
date_time_obj = datetime.datetime.strptime('2020-06-19T12:00:05.119989252Z', '%d/%m/%y %H:%M:%S')
print(date_time_obj)
