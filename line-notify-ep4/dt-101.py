import datetime
# print(datetime.datetime.now())

time_str =datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# print(time_str)
# print(type(time_str))
time_iso = datetime.datetime.now().isoformat()

with open("timeboard.txt", "w") as file:
    file.write(time_str+"\n")
    file.write(time_iso)