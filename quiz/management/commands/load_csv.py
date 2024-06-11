# myapp/management/commands/load_csv.py
import csv
from django.core.management.base import BaseCommand
from quiz.models import Quiz_Data

class Command(BaseCommand):
    help = 'Load data from CSV file into MyModel'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Quiz_Data.objects.create(
                    Question=row['Question'],
                    Category=row['Category'],
                    Correct_Answer=row['Correct_Answer'],
                    Wrong_Answer_1=row['Wrong_Answer_1'],
                    Wrong_Answer_2=row['Wrong_Answer_2'],
                    Wrong_Answer_3=row['Wrong_Answer_3'],
                    # Map all the fields accordingly
                )
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
