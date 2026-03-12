from rest_framework import serializers
from .models import Product, Cart, CartItem, Order, OrderItem, Usuario, Category
from decimal import Decimal


class CategorySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Category
        fields = ['id', 'user', 'name', 'slug']
        read_only_fields = ['slug']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Product
        fields = [
            'id', 'user', 'category', 'category_name', 'name', 
            'description', 'price', 'stock', 'image_url', 'created_at'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("O preço deve ser um valor positivo.")
        return value

class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source="product", read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta: 
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_details', 'quantity', 'subtotal']
        
    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_price']
        
    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())
    
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price_at_purchase', 'subtotal']

    def get_subtotal(self, obj):
        return obj.price_at_purchase * obj.quantity

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    date_formatted = serializers.DateTimeField(source='created_at', format="%d/%m/%Y %H:%M", read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'date_formatted', 'status', 'total_price', 'items']
        read_only_fields = ['user', 'total_price', 'status']
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password']
        
    def create(self, validated_data):
        user = Usuario.objects.create_user(**validated_data)
        return user