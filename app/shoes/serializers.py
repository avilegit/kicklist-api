from rest_framework import serializers

from core.models import Tag, Characteristic

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)

class CharacteristicsSerializer(serializers.ModelSerializer):
    """Serializer for characteristics object"""

    class Meta:
        model = Characteristic
        fields = ('id', 'name')
        read_only_fields = ('id',)
