from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Quiz_Data(models.Model):
    Question = models.TextField() #create a column called title that is a string with max length 200
    Category = models.CharField(max_length=50) #unique slug values
    Correct_Answer = models.TextField() #stores longer text than charfield
    Wrong_Answer_1 = models.CharField(max_length=50)
    Wrong_Answer_2 = models.CharField(max_length=50)
    Wrong_Answer_3 = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.Category} {self.Question}"
    

class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_category = models.CharField(max_length=50)
    percentage_correct = models.FloatField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.quiz_category} - {self.percentage_correct}%'