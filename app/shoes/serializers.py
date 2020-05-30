from rest_framework import serializers

from core.models import Tag, Characteristic, Shoes

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


class ShoeSerializer(serializers.ModelSerializer):
    """Serialize a shoe"""

    #chars and tags are foreign keys, query them
    characteristics = serializers.PrimaryKeyRelatedField(
        many = True,
        queryset=Characteristic.objects.all() 
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all() 
    )

    class Meta:
        model = Shoes
        fields = ('id', 'title', 'characteristics', 'tags', 'brand', 
                  'price', 'link')
        read_only_fields = ('id',)

class ShoeDetailSerializer(ShoeSerializer):
    """Serialize a shoe detail"""
    
    characteristics = CharacteristicsSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)