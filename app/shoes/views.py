from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Characteristic, Shoes

from shoes import serializers 

class TagViewSet(viewsets.GenericViewSet, 
                mixins.ListModelMixin,
                mixins.CreateModelMixin):
    """Manage tags in the database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user = self.request.user)

class CharacteristicViewSet(viewsets.GenericViewSet, 
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Manage ingredients in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Characteristic.objects.all()
    serializer_class = serializers.CharacteristicsSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new characteristic"""
        serializer.save(user=self.request.user)

class ShoeViewSet(viewsets.ModelViewSet):
    """Manage shoes in the db"""
    serializer_class = serializers.ShoeSerializer
    queryset = Shoes.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the shoes for the authenticated user"""
        return self.queryset.filter(user=self.request.user)
         