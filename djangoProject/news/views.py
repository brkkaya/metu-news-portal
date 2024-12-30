from django.shortcuts import render
from django.views import View

from news.models import NewsSchema


# Create your views here.
class HomePageView(View):
    template_name = 'index.html'

    def get(self, request):
        news_items = NewsSchema.objects.all()
        main_news_item = news_items[0]
        three_items_below_main = news_items[1:4]
        side_news_items = news_items[4:9]
        return render(request, self.template_name, {'main_news_item': main_news_item,
                                                    'three_items_below_main': three_items_below_main,
                                                    'side_news_items': side_news_items})


class DetailPageView(View):
    template_name = 'details.html'

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        news_item = NewsSchema.objects.get(pk=pk)
        return render(request, self.template_name, {'news_item': news_item})
