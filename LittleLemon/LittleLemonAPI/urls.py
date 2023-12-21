from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('menu-items/category', views.CategoryView.as_view()),
    path('groups/managers/users', views.ManagerListView.as_view()),
    path('groups/managers/users/<int:pk>', views.ManagerRemoveView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewListView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewRemoveView.as_view()),
    path('cart/menu-items', views.CartOperationsView.as_view()),
    path('orders', views.OrderOperationsView.as_view()),
    path('order/<int:pk>', views.SingleOrderView.as_view())
]
