from xmlrpc.client import NOT_WELLFORMED_ERROR
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Profile, Meep, Comment, Networks, NetworkMembers
from .forms import MeepForm, SignUpForm, CommentForm, CreateNetworkForm, NetworkMembersForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.forms import formset_factory
import people_also_ask

def home(request):
	meeps = Meep.objects.all().order_by("-created_at")
	r = people_also_ask.get_related_questions("how did covid start")
	print("PEOPLE ALSO ASK")
	print(r)
	return render(request, 'home.html', {"meeps":meeps, "r":r})


def profile_list(request):
	if request.user.is_authenticated:
		profiles = Profile.objects.exclude(user=request.user)
		return render(request, 'profile_list.html', {"profiles":profiles})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')

def network_list(request):
	if request.user.is_authenticated:
		networks = Networks.objects.all().order_by("-created_on")
		return render(request, 'network_list.html', {"networks":networks})
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


def createnetwork(request):
	if request.user.is_authenticated:
		template_name = 'createnetwork.html'
		form = CreateNetworkForm(request.POST or None)
		if request.method == 'POST':
			if form.is_valid():

				new_net = form.save(commit=False)
				new_net.owner = request.user
				new_net.save()

				messages.success(request, ("Added Network"))
				return editnetwork(request, new_net.id, True)
			else:
				messages.success(request, ("Couldn't add network"))
				return redirect('home')
		else:
			network_form = CreateNetworkForm()

		return render(request, template_name, {"form": network_form})


	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')



def editnetwork(request,pk, fromcreatenet=False):
	print("NET ID IS HEREEE")
	print(pk)
	if request.user.is_authenticated:
		net = get_object_or_404(Networks, id=pk)
		profiles = Profile.objects.exclude(user=request.user)

		profile_formset = formset_factory(NetworkMembersForm, extra=0)
		formset = profile_formset(initial=[{'invited': x} for x in profiles])

		checks = []
		template_name = 'editnetwork.html'
		if (request.method == 'POST') and (fromcreatenet == False):
			formset = profile_formset(request.POST)
			print("post")
			invited_list = list(formset.cleaned_data)
			p = 0
			for profile in profiles:
				form = NetworkMembersForm()
				print("profile")
				print(profile.user.username)
				new_net = form.save(commit=False)
				new_net.user = User.objects.get(username=profile)
				new_net.network = net
				new_net.invited = invited_list[p]['invited']
				new_net.save()
				p += 1


			# 	messages.success(request, ("Added Network"))
			# 	return redirect('home')
			# else:
			# 	messages.success(request, ("couldn't add network"))
			# 	return redirect('home')
			messages.success(request, ("Network member requests sent"))
			return redirect('home')
		else:
			# network_form = CreateNetworkForm()
			context = {'formset': formset,'checks': checks, 'pk': pk,}
			return render(request, template_name, context)
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')




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






def networkhighlight(request, pk):
	if request.user.is_authenticated:
		network = Networks.objects.get(id=pk)

		return render(request, "networkhighlight.html", {"network":network,})
	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')		




def notifications(request, pk):
	if request.user.is_authenticated:
		profile = Profile.objects.get(user_id=pk)
		# userobj = User.objects.get(id=pk)
		a = NetworkMembers.objects.all()
		for thing in a:
			print(thing.network.networkname)
			print("to user")
			print(thing.user)
			print("from user")
			print(thing.owner)
			print(thing.accepted)

		invited = NetworkMembers.objects.filter(user=pk, invited=True)
		print("invited")
		print(invited)
		invited_list = [inv.network.networkname for inv in invited]

		# Post Form logic
		if request.method == "POST":
			# Get current user
			current_user_profile = request.user.profile
			print(len(request.POST))
			for invite in invited:
				status = request.POST[invite.network.networkname]
				#if accepted
				if status == 'accept':
					invite.invited = False
					invite.accepted = True
					invite.save()
				if status == 'decline':
					invite.delete()
		invited = NetworkMembers.objects.filter(user=pk, invited=True)
		invited_list = [inv.network.networkname for inv in invited]
			
		return render(request, "notifications.html", {"profile":profile, "invited":invited, 'pk': pk, 'invited_list':invited_list,})
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
	