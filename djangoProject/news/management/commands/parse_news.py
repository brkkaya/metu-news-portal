import datetime
import json
from django.core.management.base import BaseCommand
from news.models import NewsSchema


class Command(BaseCommand):
    help = 'Parse a JSONL file and save its content to the NewsSchema model'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSONL file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        news_list = []
        try:
            with (open(file_path, 'r', encoding='utf-8') as file):
                for line in file:
                    try:
                        data = json.loads(line)
                        if 'date' in data:
                            try:
                                data["date"] = data["date"].replace("Updated ", "").\
                                    replace("Published ", "").\
                                    replace("Updated: ", "").\
                                    replace(" ET", "").\
                                    replace("a.m.", "AM").replace("p.m.", "PM")
                                data["date"] = datetime.datetime.strptime(data["date"], "%b. %d, %Y %I:%M %p")
                            except:
                                data["date"] = datetime.datetime.fromisoformat(data["date"])

                        news_list.append(NewsSchema(
                            title=data.get('title'),
                            content=data.get('body'),
                            img_url=data.get('img_url'),
                            url=data.get('url'),
                            date=data.get('date'),
                            topic='Science',
                            summary=data.get('answer'),
                        ))
                        self.stdout.write(self.style.SUCCESS(f"Created news item: {data.get('title')}"))
                    except json.JSONDecodeError as e:
                        self.stderr.write(self.style.ERROR(f"Error parsing line: {e}"))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error creating model object: {e}"))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected error: {e}"))

        NewsSchema.objects.bulk_create(news_list)
