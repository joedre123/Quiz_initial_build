from django.contrib import admin
from .models import Quiz_Data, QuizResult
# Register your models here.

class QuizAdmin(admin.ModelAdmin):
    list_display = ('Category','Question')
    list_filter = ('Category',) #filter on admin page

class ResultAdmin(admin.ModelAdmin):
    list_display = ('user','quiz_category','percentage_correct')
    list_filter = ('quiz_category',) #filter on admin page

admin.site.register(Quiz_Data, QuizAdmin)
admin.site.register(QuizResult, ResultAdmin)

