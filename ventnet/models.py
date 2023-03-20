from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import uuid

# create meep model
class Meep(models.Model):
	user = models.ForeignKey(
		User, related_name="meeps", 
		on_delete=models.DO_NOTHING
		)
	title = models.CharField(max_length=50)
	link = models.URLField(max_length=200, blank=True)
	# postimg = models.ImageField(upload_to='images/')
	body = models.CharField(max_length=400)
	created_at = models.DateTimeField(auto_now_add=True)
	meepid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	def __str__(self):
		return(
			f"{self.user} "
			f"({self.created_at:%Y-%m-%d %H:%M}): "
			f"{self.body}..."
			)


class Comment(models.Model):
	post = models.ForeignKey(Meep,on_delete=models.CASCADE,related_name='post')
	name = models.CharField(max_length=50)
	body = models.TextField(max_length=200)
	created_on = models.DateTimeField(auto_now_add=True)
	active = models.BooleanField(default=False)

	class Meta:
		ordering = ['created_on']

	def __str__(self):
		return 'Comment {} by {}'.format(self.body, self.name)


class Networks(models.Model):
	networkname = models.CharField(max_length=50, unique=True)
	desc = models.TextField(max_length=400)
	created_on = models.DateTimeField(auto_now_add=True)
	owner = models.CharField(max_length=50)
	private = models.BooleanField(default=False)

	class Meta:
		ordering = ['created_on']


# class NetworkNotifications(models.Model):
# 	network = models.ForeignKey(Networks, on_delete=models.CASCADE)
# 	fromuser = models.ForeignKey(User, related_name='fromuser', on_delete=models.CASCADE)
# 	touser = models.ForeignKey(User, related_name='touser',on_delete=models.CASCADE)
# 	invitedtojoin = models.BooleanField(default=False)
# 	requestedtojoin = models.BooleanField(default=False)
# 	created_on = models.DateTimeField(auto_now_add=True)

# 	class Meta:
# 		ordering = ['created_on']



# Create A User Profile Model
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	follows = models.ManyToManyField("self", 
		related_name="followed_by",
		symmetrical=False,
		blank=True)	
	
	date_modified = models.DateTimeField(User, auto_now=True)	

	def __str__(self):
		return self.user.username



class NetworkMembers(models.Model):
	network = models.ForeignKey(Networks,on_delete=models.CASCADE,related_name='network')
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	owner = models.BooleanField(default=False)
	verified = models.BooleanField(default=False)
	invited = models.BooleanField(default=False)
	accepted = models.BooleanField(default=False)
	requested = models.BooleanField(default=False)




# Create Profile When New User Signs Up
#@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		user_profile = Profile(user=instance)
		user_profile.save()
		# Have the user follow themselves
		user_profile.follows.set([instance.profile.id])
		user_profile.save()

post_save.connect(create_profile, sender=User)



