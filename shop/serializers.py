from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'name_bn', 'slug', 'image']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'name_bn', 'slug', 'category', 'price', 
                 'compare_price', 'short_description', 'short_description_bn', 'images']
    
    def get_images(self, obj):
        return [img.image.url for img in obj.images.all()]