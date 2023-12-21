from rest_framework import serializers
from .models import MenuItem, Cart, Category, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta():
        model = Category
        fields = ['title']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        depth = 0
        

class CartHelpSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['id', 'title', 'price']


class CartSerializer(serializers.ModelSerializer):
    menuitem = CartHelpSerializer()
    class Meta():
        model = Cart
        fields = ['menuitem', 'quantity', 'price']


class CartAddSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['menuitem', 'quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }

    
class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['menuitem']


class OrderSerializer(serializers.ModelSerializer):
    class Meta():
        model = Order
        fields = ['id', 'user', 'total', 'delivery_crew', 'status', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = OrderItem
        fields = ['order','menuitem', 'quantity', 'unit_price', 'price']


class SingleHelperSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['title', 'price']


class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = SingleHelperSerializer
    class Meta():
        model = OrderItem
        fields = ['menuitem', 'quantity']


class OrderCrewSerializer(serializers.ModelSerializer):
    class Meta():
        model = Order
        fields = ['delivery_crew']
        

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id', 'username', 'email']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']