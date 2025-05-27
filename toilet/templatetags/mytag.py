from django.utils import timezone
from django import template
register = template.Library()

@register.filter(name="time_since")
def time_since(value):
    "timesince処理を以下に記載する（カスタムで作成）"
    now = timezone.localtime(timezone.now())
    date = timezone.localtime(value)

    seconds = int((now - date).total_seconds())

    print(seconds)

    if seconds < 60:
        seconds = str(seconds)
        return f"{seconds}秒"
    minutes = seconds // 60
    if minutes < 60:
        minutes = str(minutes)
        return f"{minutes}分"
    hours = minutes // 60
    if hours < 24:
        hours = str(hours)
        return f"{hours}時間"
    days = hours // 24
    if days < 7:
        days = str(days)
        return f"{days}日"
    weeks = days // 7
    if weeks < 5:
        weeks = str(weeks)
        return f"{weeks}週間"
    months = days // 30
    if months < 12:
        months = str(months)
        return f"{months}ヶ月"
    years = days // 365

    return str(years)
    