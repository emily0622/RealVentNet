from xmlrpc.client import NOT_WELLFORMED_ERROR
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile, Meep, Comment
from .forms import MeepForm, SignUpForm, CommentForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

def home(request):
	meeps = Meep.objects.all().order_by("-created_at")
	return render(request, 'home.html', {"meeps":meeps})


def profile_list(request):
	if request.user.is_authenticated:
		profiles = Profile.objects.exclude(user=request.user)
		return render(request, 'profile_list.html', {"profiles":profiles})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')

def add_ventpost(request):
	if request.user.is_authenticated:
		form = MeepForm(request.POST or None)
		if request.method == "POST":
			if form.is_valid():
				meep = form.save(commit=False)
				meep.user = request.user
				meep.save()
				messages.success(request, ("Your Meep Has Been Posted!"))
				return redirect('home')
		return render(request, 'add_ventpost.html', {"form":form})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')

def venthighlight(request, slug):
	template_name = 'venthighlight.html'
	post = get_object_or_404(Meep, meepid=slug)
	comments = Comment.objects.filter(post=post).order_by("-created_on")
	# comments = Comment.objects.all()
	# comments = get_object_or_404(Comment, post=)
	# comment_object = get_object_or_404(Comment, post=post)
	# comments = comment_object.comments.filter(active=True)

	return render(request, template_name, {'post': post,
											'comments': comments})



def addcomment(request, slug):
	template_name = 'addcomment.html'
	post = get_object_or_404(Meep, meepid=slug)
	new_comment = None
	# Comment posted
	if request.method == 'POST':
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():

			# Create Comment object but don't save to database yet
			new_comment = comment_form.save(commit=False)
			# Assign the current post to the comment
			new_comment.post = post
			new_comment.name = request.user
			# Save the comment to the database
			new_comment.save()
			# redirect_url = "venthighlight/" + slug
			# return redirect(redirect_url)
			# return venthighlight(request, slug)
			messages.success(request, ("Added comment"))
			return venthighlight(request, slug)
		else:
			messages.success(request, ("couldn;t add comment"))
			return venthighlight(request, slug)
	else:
		comment_form = CommentForm()


	return render(request, template_name, {'post': post,
											'new_comment': new_comment,
											'comment_form': comment_form})



def profile(request, pk):
	if request.user.is_authenticated:
		profile = Profile.objects.get(user_id=pk)
		meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")

		# Post Form logic
		if request.method == "POST":
			# Get current user
			current_user_profile = request.user.profile
			# Get form data
			action = request.POST['follow']
			# Decide to follow or unfollow
			if action == "unfollow":
				current_user_profile.follows.remove(profile)
			elif action == "follow":
				current_user_profile.follows.add(profile)
			# Save the profile
			current_user_profile.save()



		return render(request, "profile.html", {"profile":profile, "meeps":meeps})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')		



def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, ("You Have Been Logged In!  Get MEEPING!"))
			return redirect('home')
		else:
			messages.success(request, ("There was an error logging in. Please Try Again..."))
			return redirect('login')

	else:
		return render(request, "login.html", {})


def logout_user(request):
	logout(request)
	messages.success(request, ("You Have Been Logged Out. Sorry to Meep You Go..."))
	return redirect('home')

def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# first_name = form.cleaned_data['first_name']
			# second_name = form.cleaned_data['second_name']
			# email = form.cleaned_data['email']
			# Log in user
			user = authenticate(username=username, password=password)
			login(request,user)
			messages.success(request, ("You have successfully registered! Welcome!"))
			return redirect('home')
	
	return render(request, "register.html", {'form':form})


def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		form = SignUpForm(request.POST or None, instance=current_user)
		if form.is_valid():
			form.save()
			login(request, current_user)
			messages.success(request, ("Your Profile Has Been Updated!"))
			return redirect('home')

		return render(request, "update_user.html", {'form':form})
	else:
		messages.success(request, ("You Must Be Logged In To View That Page..."))
		return redirect('home')
	