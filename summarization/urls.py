from django.urls import path
from .views import summariztion_passed_hourd_average, summariztion_hourly_average, summariztion_daily_average, summariztion_monthly_average, summariztion_yearly_average

urlpatterns = [
	path('api/<int:hour>/passed-average', summariztion_passed_hourd_average, name='passed_hourd_average'),
	path('api/<int:hour>/average', summariztion_hourly_average, name='hourly_average'),
	path('api/<int:year>/<int:month>/average', summariztion_monthly_average, name='monthly_average'),
	path('api/<int:year>/<int:month>/<int:day>/average', summariztion_daily_average, name='daily_average'),
	path('api/<int:year>/average-year', summariztion_yearly_average, name='yearly_average'),
]
