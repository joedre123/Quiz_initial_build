from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from django.template.loader import render_to_string
from .models import Quiz_Data, QuizResult
import pandas as pd
from django.db import IntegrityError
from django.utils import timezone
#from quiz_project.settings import EXCEL_FILE_PATH

EXCEL_FILE_PATH = 'C:/Users/JosephDrewry/OneDrive - 4Most/Training/Python Training/Quiz_project/quiz/static/quiz/quiz_data.csv'
# Create your views here.


quiz_types = {
    'Geography': "Test your geography knowledge!",
    "History": "Test your history knowledge!",
    "General": "Test your general knowledge!",
    "Sport": "Test your sport knowledge!",
    "Music": "Test your music knowledge!",
}

def load_quiz_data(request):
    if not Quiz_Data.objects.exists():
        df = pd.read_csv(EXCEL_FILE_PATH)
        Quiz_Data.objects.all().delete()
        for index, row in df.iterrows():
            Quiz_Data.objects.create(
                Question=row['Question'],
                    Category=row['Category'],
                    Correct_Answer=row['Correct_Answer'],
                    Wrong_Answer_1=row['Wrong_Answer_1'],
                    Wrong_Answer_2=row['Wrong_Answer_2'],
                    Wrong_Answer_3=row['Wrong_Answer_3'],
            )


def index(request):
    load_quiz_data(request)
    quiz_items = []
    for quiz, description in quiz_types.items():
        quiz_path = reverse("quiz", args=[quiz])  # Assuming you have defined the URL pattern correctly
        quiz_items.append({'name': quiz.capitalize(), 'path': quiz_path, 'description': description})

    register_url = reverse('register')  # Get the URL for the login page
    login_url = reverse('login')  # Get the URL for the login page
    leaderboard_url = reverse('leaderboard')  # Get the URL for the login page
    context = {'quiz_items': quiz_items,
               'login_url': login_url,  # Include the login URL in the context
               'register_url': register_url,  # Include the login URL in the context
               'leaderboard_url': leaderboard_url,  # Include the login URL in the context
               }
    return render(request, 'quiz/index.html', context)

def register(request):
    home_url = reverse('all-quizes')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        context = {'form' : form,
                   'home_url' : home_url
        }
        #print('form ' + str(form))
        if form.is_valid():
            try:
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('all-quizes')  # Redirect to the homepage after registration
            except IntegrityError:
                form.add_error('username', 'Username already exists.')
        
    else:
        form = UserCreationForm()
        context = {'form' : form,
                   'home_url' : home_url
        }
        #print('form2 ' + str(form))
    return render(request, 'quiz/register.html', context)

def user_login(request):
    home_url = reverse('all-quizes')
    register_url = reverse('register')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                context = {
                    'form': form,
                    'home_url': home_url,
                    'register_url' : register_url,
                        }
                return redirect('all-quizes')  # Redirect to the homepage after login
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
        'home_url': home_url,
        'register_url' : register_url,
    }
    return render(request, 'quiz/login.html', context)



def quizes(request, quiz):
    #quiz_data = Quiz_Data.objects.all()
    #print('quiz' + str(quiz))
    home_url = reverse('all-quizes')
    try:
        print('requested quiz ' + str(quiz))
        challenge_text = quiz_types[quiz.capitalize()]
        quiz_data = Quiz_Data.objects.all()#filter(Category=quiz)
        print(f"Loaded {quiz_data.count()} quiz questions")

        if request.method == "POST":
            answers = []
            number_correct = 0
            number_questions = 0
            #print('Category' + str(Category))
            for key, value in request.POST.items():
                if key.startswith('answer_'):
                    question_id = request.POST.get(f'question_id_{key.split("_")[1]}')
                    question = get_object_or_404(Quiz_Data, id=question_id)
                    user_answer = value
                    correct_answer = question.Correct_Answer
                    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
                    if is_correct:
                        number_correct += 1
                    number_questions += 1
                    percentage_correct = round((number_correct / number_questions) * 100,1) if number_questions > 0 else 0
                    answers.append({
                        'question': question.Question,
                        'user_answer': user_answer,
                        'correct_answer': correct_answer,
                        'is_correct': is_correct,
                    })
            
            # Save the quiz result
            QuizResult.objects.create(
                user=request.user,
                quiz_category=quiz.capitalize(),
                percentage_correct=percentage_correct,
                date_taken=timezone.now()
            )

            context = {'quiz': quiz, 
                   'challenge_text': challenge_text,
                   'quiz_data': quiz_data,
                   'answers': answers,
                   'percentage_correct': percentage_correct,
                   'submitted': True,
                   'home_url' : home_url,
                   }
            print(f"Context for POST: {context}")
            return render(request, 'quiz/quiz-details.html', context)
                      #{ "context":=context, "quiz_data":=quiz_data })
        context = {
            'challenge_text': challenge_text,
            'quiz': quiz.capitalize(),  # Capitalize quiz before passing to the context
            'quiz_data': quiz_data,
            'submitted': False,
            'home_url' : home_url,
        }
        return render(request, 'quiz/quiz-details.html', context)   
    except KeyError as e:
        print(f"Error: {e}")
        return HttpResponse()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return HttpResponse("<h1>An unexpected error occurred!</h1>")  
       

#create a view for the leaderboard
def leaderboard(request):
    home_url = reverse('all-quizes')
    results = QuizResult.objects.all().order_by('-percentage_correct', 'date_taken')
    categories = QuizResult.objects.values_list('quiz_category', flat=True).distinct()
    selected_category = request.GET.get('category', '')

    if selected_category == "":
        results = QuizResult.objects.all()
    else:
        results = QuizResult.objects.filter(quiz_category=selected_category)
    context = {'results': results,
               'home_url' : home_url,
               'categories' : categories,
               'selected_category' : selected_category,
               }
    return render(request, 'quiz/leaderboard.html', context)




'''
class Quiz_Data(models.Model):
    Question = models.TextField() #create a column called title that is a string with max length 200
    Category = models.CharField(max_length=50) #unique slug values
    Correct_Answer = models.TextField() #stores longer text than charfield
    Wrong_Answer_1 = models.CharField(max_length=50)
    Wrong_Answer_2 = models.CharField(max_length=50)
    Wrong_Answer_3 = models.CharField(max_length=50)'''