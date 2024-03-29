from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('profile_list/', views.profile_list, name='profile_list'),
    path('network_list/', views.network_list, name='network_list'),
    path('add_ventpost/', views.add_ventpost, name='add_ventpost'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('venthighlight/<slug:slug>', views.venthighlight, name='venthighlight'),
    # path('venthighlight/', views.venthighlight, name='venthighlight'),
    path('addcomment/<slug:slug>', views.addcomment, name='addcomment'),
    path('addpromt/<slug:slug>', views.addpromt, name='addpromt'),
    path('createnetwork/', views.createnetwork, name='createnetwork'),
    path('editnetwork/<slug:pk>', views.editnetwork, name='editnetwork'),
    path('networkhighlight/<slug:pk>', views.networkhighlight, name='networkhighlight'),
    path('notifications/<int:pk>', views.notifications, name='notifications'),
    path('login/', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('update_user/', views.update_user, name='update_user'),
]
