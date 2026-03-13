from django.shortcuts import render
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Cart, CartItem, Order, OrderItem, Usuario, Category
from .serializers import (
    ProductSerializer, CartSerializer, CartItemSerializer, 
    OrderItemSerializer, OrderSerializer, UserRegistrationSerializer, 
    CategorySerializer
)
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny]) 
def ping_despertador(request):
    return Response({"status": "online", "message": ":)"})


class RegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.filter(user=self.request.user)
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id, user=request.user)
        except Product.DoesNotExist:
            return Response({'error': 'Produto não encontrado no seu sandbox'}, status=status.HTTP_404_NOT_FOUND)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
            
        item.save()
        return Response({'status': 'Quantidade atualizada no carrinho'}, status=status.HTTP_201_CREATED)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.select_related('product').all()
            if not cart_items.exists():
                return Response({"error": "Carrinho vazio"}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": "Carrinho não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            total_price = sum(item.product.price * item.quantity for item in cart_items)
            order = Order.objects.create(user=request.user, total_price=total_price)

            for item in cart_items:
                product = item.product
                
                if product.stock < item.quantity:
                    raise ValidationError(f"Estoque insuficiente para {product.name}")

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price_at_purchase=product.price 
                )

                product.stock -= item.quantity
                product.save()

            cart_items.delete() 

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
