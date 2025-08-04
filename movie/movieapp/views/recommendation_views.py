# movieapp/views/recommendation_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from movieapp.models import Movie, FavoriteMovie, Genre
from movieapp.serializers import MovieSerializer

class RecommendationView(APIView):
    """View for recommending movies based on user favorites."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Generate movie recommendations for the authenticated user.
        
        Returns:
            Response: List of recommended movies.
        """
        user = request.user
        favorite_genres = Genre.objects.filter(
            movie__favoritemovie__user=user
        ).distinct()
        recommended_movies = Movie.objects.filter(
            genres__in=favorite_genres
        ).exclude(
            favoritemovie__user=user
        ).order_by('?')[:10]
        serializer = MovieSerializer(recommended_movies, many=True)
        return Response(serializer.data)