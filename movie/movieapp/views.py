from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Movie
from .serializers import MovieSerializer

class MovieViewSet(viewsets.ModelViewSet):
      queryset = Movie.objects.all()
      serializer_class = MovieSerializer
      permission_classes = [IsAuthenticatedOrReadOnly]

  # Add authentication views
token_obtain_pair = TokenObtainPairView.as_view()
token_refresh = TokenRefreshView.as_view()