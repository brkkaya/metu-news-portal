from django.shortcuts import render
from django.views import View

from news.embedding_service import EmbeddingService
from news.models import NewsSchema
from news.reranker_service import RerankerService
from news.utilities import convert_faiss_to_document
from news.vector_db import Engine

reranker = RerankerService("BAAI/bge-reranker-v2-m3")
vector_db = Engine("faiss_news_portal", EmbeddingService("BAAI/bge-m3"), reranker=reranker)


# Create your views here.
class HomePageView(View):
    template_name = 'index.html'

    def get(self, request):
        query = self.request.GET.get('query', '')  # Get 'query' from URL
        if query:
            documents = vector_db.search(query, 9)
            response = [convert_faiss_to_document(document) for document in documents]
            main_news_item = response[0]
            three_items_below_main = response[1:4]
            side_news_items = response[4:9]
        else:
            news_items = NewsSchema.objects.order_by('?')
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


class RecommendResultsView(View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        documents = vector_db.recommend("dereli_irem")
        response = [convert_faiss_to_document(document) for document in documents]
        main_news_item = response[0]
        three_items_below_main = response[1:4]
        side_news_items = response[4:9]
        return render(request, self.template_name, {'main_news_item': main_news_item,
                                                    'three_items_below_main': three_items_below_main,
                                                    'side_news_items': side_news_items})
