"""
Views for the Reviews app.
"""

from django.db.models import Avg, Count
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Review
from .permissions import IsReviewOwner, IsReviewTarget
from .serializers import (
    ReviewCreateSerializer,
    ReviewFlagSerializer,
    ReviewModerateSerializer,
    ReviewResponseSerializer,
    ReviewSerializer,
    ReviewStatsSerializer,
    ReviewUpdateSerializer,
)


class ReviewViewSet(ModelViewSet):
    """
    ViewSet for Review CRUD operations.
    """
    queryset = Review.objects.select_related(
        'ride', 'reviewer', 'target'
    ).filter(is_visible=True)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReviewUpdateSerializer
        elif self.action == 'respond':
            return ReviewResponseSerializer
        elif self.action == 'flag':
            return ReviewFlagSerializer
        elif self.action == 'moderate':
            return ReviewModerateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsReviewOwner()]
        elif self.action == 'respond':
            return [permissions.IsAuthenticated(), IsReviewTarget()]
        elif self.action == 'moderate':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Filter reviews based on query parameters.
        """
        queryset = Review.objects.select_related(
            'ride', 'reviewer', 'target'
        ).filter(is_visible=True)
        
        # Staff can see all reviews including hidden
        if self.request.user.is_staff:
            show_hidden = self.request.query_params.get('show_hidden')
            if show_hidden and show_hidden.lower() == 'true':
                queryset = Review.objects.select_related(
                    'ride', 'reviewer', 'target'
                ).all()
        
        # Filter by ride
        ride_id = self.request.query_params.get('ride_id')
        if ride_id:
            queryset = queryset.filter(ride_id=ride_id)
        
        # Filter by target user
        target_id = self.request.query_params.get('target_id')
        if target_id:
            queryset = queryset.filter(target_id=target_id)
        
        # Filter by review type
        review_type = self.request.query_params.get('review_type')
        if review_type:
            queryset = queryset.filter(review_type=review_type)
        
        # Filter by minimum rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=int(min_rating))
        
        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def my_reviews_given(self, request):
        """
        Get all reviews given by the current user.
        """
        reviews = Review.objects.filter(
            reviewer=request.user
        ).select_related('ride', 'target')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_reviews_received(self, request):
        """
        Get all reviews received by the current user.
        """
        reviews = Review.objects.filter(
            target=request.user,
            is_visible=True
        ).select_related('ride', 'reviewer')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get review statistics for a user.
        """
        user_id = request.query_params.get('user_id', request.user.id)
        
        reviews = Review.objects.filter(
            target_id=user_id,
            is_visible=True
        )
        
        # Calculate stats
        stats = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        # Rating distribution
        distribution = {}
        for i in range(1, 6):
            distribution[str(i)] = reviews.filter(rating=i).count()
        
        stats['rating_distribution'] = distribution
        stats['average_rating'] = stats['average_rating'] or 0
        
        serializer = ReviewStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """
        Add a response to a review (by the reviewed user).
        """
        review = self.get_object()
        
        if review.target != request.user:
            return Response(
                {'detail': 'You can only respond to reviews about you.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if review.response:
            return Response(
                {'detail': 'You have already responded to this review.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        review.add_response(serializer.validated_data['response'])
        
        return Response({
            'message': 'Response added successfully.',
            'review': ReviewSerializer(review).data
        })

    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        """
        Flag a review for moderation.
        """
        review = self.get_object()
        
        serializer = ReviewFlagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        review.flag(serializer.validated_data['reason'])
        
        return Response({
            'message': 'Review flagged for moderation.',
        })

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser]
    )
    def moderate(self, request, pk=None):
        """
        Moderate a flagged review (admin only).
        """
        review = self.get_object()
        
        serializer = ReviewModerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        review.moderate(
            moderator=request.user,
            is_visible=serializer.validated_data['is_visible']
        )
        
        return Response({
            'message': 'Review moderated successfully.',
            'review': ReviewSerializer(review).data
        })

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAdminUser]
    )
    def flagged(self, request):
        """
        Get all flagged reviews (admin only).
        """
        reviews = Review.objects.filter(
            is_flagged=True
        ).select_related('ride', 'reviewer', 'target')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

