"""
Views for the Drivers app.
"""

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Driver, DriverDocument
from .permissions import IsDriverOwner, IsDriverOrReadOnly
from .serializers import (
    DriverCreateSerializer,
    DriverDocumentCreateSerializer,
    DriverDocumentReviewSerializer,
    DriverDocumentSerializer,
    DriverSerializer,
    DriverUpdateSerializer,
)


class DriverViewSet(ModelViewSet):
    """
    ViewSet for Driver CRUD operations.
    """
    queryset = Driver.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticated, IsDriverOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return DriverCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DriverUpdateSerializer
        return DriverSerializer

    def get_queryset(self):
        """
        Filter queryset based on query parameters.
        """
        queryset = Driver.objects.select_related('user').filter(is_active=True)
        
        # Filter by verification status
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        # Filter by minimum rating
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=float(min_rating))
        
        return queryset

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get the current user's driver profile.
        """
        try:
            driver = Driver.objects.select_related('user').get(user=request.user)
            serializer = DriverSerializer(driver)
            return Response(serializer.data)
        except Driver.DoesNotExist:
            return Response(
                {'detail': 'You do not have a driver profile.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """
        Get all documents for a driver.
        """
        driver = self.get_object()
        
        # Only allow driver owner or staff to see documents
        if driver.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You do not have permission to view these documents.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        documents = driver.documents.all()
        serializer = DriverDocumentSerializer(documents, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAdminUser],
    )
    def verify(self, request, pk=None):
        """
        Admin action to verify a driver profile.
        Marks the driver as verified and activates them.
        """
        driver = self.get_object()

        driver.is_verified = True
        driver.is_active = True
        driver.save(update_fields=['is_verified', 'is_active', 'updated_at'])

        return Response(DriverSerializer(driver).data)

    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """
        Upload a new document for the driver.
        """
        driver = self.get_object()
        
        # Only allow driver owner to upload documents
        if driver.user != request.user:
            return Response(
                {'detail': 'You can only upload documents for your own profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DriverDocumentCreateSerializer(
            data=request.data,
            context={'driver': driver}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DriverProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating the current user's driver profile.
    """
    permission_classes = [permissions.IsAuthenticated, IsDriverOwner]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DriverUpdateSerializer
        return DriverSerializer

    def get_object(self):
        return Driver.objects.select_related('user').get(user=self.request.user)


class BecomeDriverView(generics.CreateAPIView):
    """
    API endpoint for a user to become a driver.
    """
    serializer_class = DriverCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if user already has a driver profile
        if hasattr(request.user, 'driver_profile'):
            return Response(
                {'detail': 'You already have a driver profile.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)


class DriverDocumentViewSet(ModelViewSet):
    """
    ViewSet for Driver Documents.
    """
    queryset = DriverDocument.objects.select_related('driver', 'driver__user').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return DriverDocumentCreateSerializer
        elif self.action == 'review':
            return DriverDocumentReviewSerializer
        return DriverDocumentSerializer

    def get_queryset(self):
        """
        Filter documents - users can only see their own, staff can see all.
        """
        user = self.request.user
        if user.is_staff:
            return DriverDocument.objects.select_related('driver', 'driver__user').all()
        
        if hasattr(user, 'driver_profile'):
            return DriverDocument.objects.filter(driver=user.driver_profile)
        
        return DriverDocument.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def review(self, request, pk=None):
        """
        Admin endpoint to review a document.
        """
        document = self.get_object()
        serializer = DriverDocumentReviewSerializer(
            document,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        document.status = serializer.validated_data['status']
        document.rejection_reason = serializer.validated_data.get('rejection_reason', '')
        document.reviewed_at = timezone.now()
        document.reviewed_by = request.user
        document.save()
        
        return Response(DriverDocumentSerializer(document).data)

