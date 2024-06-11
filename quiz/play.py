from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from .models import Quiz_Data
import pandas as pd

EXCEL_FILE_PATH = 'C:/Users/JosephDrewry/OneDrive - 4Most/Training/Python Training/Quiz_project/quiz/static/quiz/quiz_data.csv'

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

def homepage(request):
    return load_quiz_data(request)

def index(request):
    load_quiz_data(request)
    quiz_items = []
    for quiz, description in quiz_types.items():
        quiz_path = reverse("quiz", args=[quiz])  # Assuming you have defined the URL pattern correctly
        quiz_items.append({'name': quiz.capitalize(), 'path': quiz_path, 'description': description})
    context = {'quiz_items': quiz_items}
    return render(request, 'quiz/index.html', context)

def quizes(request, quiz):
    try:
        print(f"Requested quiz: {quiz}")
        challenge_text = quiz_types[quiz.capitalize()]
        quiz_data = Quiz_Data.objects.filter(Category__iexact=quiz)  # Case-insensitive filtering
        print(f"Loaded {quiz_data.count()} quiz questions")

        if request.method == "POST":
            answers = []
            for key, value in request.POST.items():
                if key.startswith('answer_'):
                    question_id = request.POST.get(f'question_id_{key.split("_")[1]}')
                    question = get_object_or_404(Quiz_Data, id=question_id)
                    user_answer = value
                    correct_answer = question.Correct_Answer
                    is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
                    answers.append({
                        'question': question.Question,
                        'user_answer': user_answer,
                        'correct_answer': correct_answer,
                        'is_correct': is_correct,
                    })
            context = {
                'quiz': quiz,
                'challenge_text': challenge_text,
                'quiz_data': quiz_data,
                'answers': answers,
                'submitted': True,
            }
            print(f"Context for POST: {context}")
            return render(request, 'quiz/quiz-details.html', context)

        context = {
            'challenge_text': challenge_text,
            'quiz': quiz.capitalize(),
            'quiz_data': quiz_data,
            'submitted': False,
        }
        print(f"Context for GET: {context}")
        return render(request, 'quiz/quiz-details.html', context)
    except KeyError as e:
        print(f"Error: {e}")
        return HttpResponseNotFound("<h1>This quiz is not supported!</h1>")
    except Exception as e:
        print(f"Unexpected error: {e}")
        return HttpResponse("<h1>An unexpected error occurred!</h1>")
