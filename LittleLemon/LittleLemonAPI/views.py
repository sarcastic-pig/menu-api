from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound 
from .models import MenuItem, Cart, Order, OrderItem, Category
from rest_framework import generics, permissions
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import MenuItemSerializer, CartSerializer, CartAddSerializer, OrderSerializer, CategorySerializer, EmployeeSerializer, UserSerializer, CartRemoveSerializer, SingleOrderSerializer, OrderCrewSerializer
from .paginations import MenuItemListPagination
from .permissions import IsDeliveryCrew, IsManager
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'category__title']
    ordering_fields = ['price','category']
    pagination_class = MenuItemListPagination

    def get_permissions(self):
        permission_classes = []
        if self.request.method != "GET":
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]        

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == "PATCH":
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        if self.request.method == "DELETE":
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def patch(self, request, *args, **kwargs):
        menuitem = MenuItem.objects.get(pk=self.kwargs['pk'])
        menuitem.featured = not menuitem.featured
        menuitem.save()
        return JsonResponse(status=200, data={'message': 'Featured status of {} changed to {}'.format(str(menuitem.title), str(menuitem.featured))})

class CategoryView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated]


class ManagerListView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Managers')
            managers.user_set.add(user)
            return JsonResponse(status=201, data={'message':'User was added to Manager group!'})

    
class ManagerRemoveView(generics.DestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def delete(self):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='Managers')
        managers.user_set.remove(user)
        return JsonResponse(status=200, data={'message':'User was removed from Manager Group'})
        

class DeliveryCrewListView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name="Delivery Crew")
            delivery_crew.user_set.add(user)
            return JsonResponse(status=201, data={'message':'User was added to Delivery Crew!'})
        

class DeliveryCrewRemoveView(generics.DestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = User.objects.filter(groups__name='Delivery Crew')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def delete(self):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        delivery_crew = Group.objects.get(name='Delivery Crew')
        delivery_crew.user_set.remove(user)
        return JsonResponse(status=200, data={'message': 'User was removed from Delivery Crew.'})

class CartOperationsView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        return cart
    
    def post(self, request, *args, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price, menuitem_id=id)
        except:
            return JsonResponse(status=409, data ={'message':'Item already in cart'})
        return JsonResponse(status=201, data={'message':'Item added to cart!'})
        
    def delete(self, request, *arg, **kwargs):
        if request.data['menuitem']:
            serialized_item = CartRemoveSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            menuitem = request.data['menuitem']
            cart = get_object_or_404(Cart, user=request.user, menuitem=menuitem)
            cart.delete()
        else:
            Cart.objects.filter(user = request.user).delete()
            return JsonResponse(status=201, data={'message':'Items removed from cart'})
        

class OrderOperationsView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = OrderSerializer
    permissions_class = []

    def get_queryset(self):
        if self.request.user.groups.filter(name="Managers").exists() or self.request.user.is_superuser == True:
            query = Order.objects.all()
        elif self.request.user.groups.filter(name="Delivery Crew").exists():
            query = Order.objects.filter(delivery_crew=self.request.user)
        else:
            query = Order.objects.filter(user=self.request.user)
        return query
    
    def get_permissions(self):
        if self.request.method == "GET" or "POST":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
    

    def post(self, request):
        cart = Cart.objects.filter(user=request.user)
        order = Order.objects.create(user=request.user, status=False)
        for i in cart.values():
            menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
            orderitem = OrderItem.objects.create(order=order, menuitem=menuitem, quantity=i['quantity'])
            orderitem.save()
        cart.delete()
        return JsonResponse(status=201, data={'message':'Order created'})
    

class SingleOrderView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    serializer_class = SingleOrderSerializer

    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.user == order.user and self.request.method == "GET":
            permission_classes = [IsAuthenticated]
        elif self.request.method == "PUT" or self.request.method == "DELETE":
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsDeliveryCrew | IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self, request, *args, **kwargs):
        query = OrderItem.objects.filter(order_id=self.kwargs['pk'])
        return query
    
    def patch(self, request):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return JsonResponse(status = 200, data={'message':'order updated'})
    
    def put(self, request):
        serialized_item = OrderCrewSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.data['delivery_crew']
        order = get_object_or_404(Order, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return JsonResponse(status=201, data={'message': 'delivery crew assigned'})
    
    def delete(self, request):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return JsonResponse(status=200, data={'message':'Order #{} was deleted'.format(order_number)})
