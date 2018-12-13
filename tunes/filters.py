from django_filters import FilterSet, CharFilter

from .models import Tune


class TuneFilter(FilterSet):
    artist = CharFilter(lookup_expr='icontains')
    title = CharFilter(lookup_expr='icontains')
    album = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Tune
        fields = []
