import datetime as dt

# today = datetime.date.today()
# end_date = datetime.date(2026,1,16)
# difference = end_date - today

due_data = '2026-01-20'
print(dt.datetime.strptime(due_data, "%Y-%m-%d").date())

