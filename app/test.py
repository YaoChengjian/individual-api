from datetime import date, timedelta

today = date.today()
tomorrow = date.today() + timedelta(days=1)
half_year_later = date(today.year + (today.month + 6 - 1) // 12, (today.month + 6 - 1) % 12 + 1, 1)
one_year_later = date(today.year + 1, today.month, 1)

print(today, tomorrow, half_year_later, one_year_later)