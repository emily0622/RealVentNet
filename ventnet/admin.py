from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile, Meep, Comment

# Unregister Groups
admin.site.unregister(Group)

# Mix Profile info into User info
class ProfileInline(admin.StackedInline):
	model = Profile

# Extend User Model
class UserAdmin(admin.ModelAdmin):
	model = User
	# Just display username fields on admin page
	fields = ["username"]
	inlines = [ProfileInline]


admin.site.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	#find og for the following line
	list_display = ('name', 'body', 'post', 'created_on','active')
	list_filter = ('active', 'created_on')
	search_fields = ('name', 'body')
	actions = ['approve_comments']

	def approve_comments(self, request, queryset):
		queryset.update(active=True)


# Unregister initial User
admin.site.unregister(User)

# Reregister User and Profile
admin.site.register(User, UserAdmin)
#admin.site.register(Profile)

# Register Meeps
admin.site.register(Meep)