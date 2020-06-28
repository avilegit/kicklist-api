from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the shoes for the authenticated user"""
        tags = self.request.query_params.get('tags')
        characteristics = self.request.query_params.get('characteristics')

        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if characteristics:
            characteristic_ids = self._params_to_ints(characteristics)
            queryset = queryset.filter(characteristics__id__in=characteristic_ids)

        return self.queryset.filter(user=self.request.user)
         
    def get_serializer_class(self):
        """Return approrpiate serializer class"""
        if self.action == 'retrieve':
            return serializers.ShoeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.ShoeImageSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new shoe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a shoe"""
        shoe = self.get_object()
        serializer = self.get_serializer(
            shoe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
