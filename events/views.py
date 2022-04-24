from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from events.models import Event, Comment, Fav, Donation
from events.owner import OwnerListView, OwnerDetailView, OwnerDeleteView
from events.forms import CreateForm, CommentForm, DonationForm
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q

# Create your views here.

#class EventListView(OwnerListView):
#    model = Event
#    # By convention:
#    # template_name = "events/event_list.html"

#class EventDetailView(OwnerDetailView):
#    model = Event

#class EventCreateView(OwnerCreateView):
#    model = Event
#    # List the fields to copy from the Event model to the Event form
#    fields = ['title', 'price', 'text']

#class EventUpdateView(OwnerUpdateView):
#    model = Event
#    fields = ['title', 'price', 'text']
#    # This would make more sense
#    # fields_exclude = ['owner', 'created_at', 'updated_at']

class EventListView(OwnerListView):
    model = Event
    template_name = "events/event_list.html"

    def get(self, request):
        favorites = list()
        strval =  request.GET.get("search", False)
        if strval:
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            # __icontains for case-insensitive search
            query = Q(performer__icontains=strval) 
            #query.add(Q(text__icontains=strval), Q.OR)
            #query.add(Q(tags__name__icontains=strval), Q.OR)
            #event_list = Event.objects.filter(query).select_related().order_by('-updated_at')[:10]
            event_list = Event.objects.filter(query).select_related().order_by('showtime')[:10]
        else:
            #post_list = Post.objects.all().order_by('-updated_at')[:10]
            event_list = Event.objects.all()
            if request.user.is_authenticated:
                # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
                rows = request.user.favorite_events.values('id')
                # favorites = [2, 4, ...] using list comprehension
                favorites = [ row['id'] for row in rows ]

        # Augment the event_list
        for obj in event_list:
            obj.natural_updated = naturaltime(obj.updated_at)

        ctx = {'event_list' : event_list, 'favorites': favorites, 'search': strval}
        return render(request, self.template_name, ctx)

class EventDetailView(OwnerDetailView):
    model = Event
    template_name = "events/event_detail.html"
    def get(self, request, pk) :
        x = Event.objects.get(id=pk)
        #comments = Comment.objects.filter(event=x).order_by('-updated_at')
        #comment_form = CommentForm()
        #context = { 'event' : x, 'comments': comments, 'comment_form': comment_form }
        donations = Donation.objects.filter(event=x).order_by('-updated_at')
        donation_form = DonationForm()
        context = { 'event' : x, 'donations': donations, 'donation_form': donation_form }
        return render(request, self.template_name, context)

class EventCreateView(LoginRequiredMixin, View):
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('pics:all')

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        pic = form.save(commit=False)
        pic.owner = self.request.user
        pic.save()

        # Adjust the model owner before saving
        inst = form.save(commit=False)
        inst.owner = self.request.user
        inst.save()
        # https://django-taggit.readthedocs.io/en/latest/forms.html#commit-false
        form.save_m2m()

        return redirect(self.success_url)

class EventUpdateView(LoginRequiredMixin, View):
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('pics:all')

    def get(self, request, pk):
        pic = get_object_or_404(Event, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        pic = get_object_or_404(Event, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=pic)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        pic = form.save(commit=False)
        pic.save()

        # Adjust the model owner before saving
        inst = form.save(commit=False)
        inst.owner = self.request.user
        inst.save()
        # https://django-taggit.readthedocs.io/en/latest/forms.html#commit-false
        form.save_m2m()

        return redirect(self.success_url)

class EventDeleteView(OwnerDeleteView):
    model = Event

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        a = get_object_or_404(Event, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, event=a)
        comment.save()
        return redirect(reverse('events:event_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "events/comment_delete.html"
    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        event = self.object.event
        return reverse('events:event_detail', args=[event.id])

class DonationCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        a = get_object_or_404(Event, id=pk)
        donation = Donation(amount=request.POST['donation'], owner=request.user, event=a)
        donation.save()
        return redirect(reverse('events:event_detail', args=[pk]))

class DonationDeleteView(OwnerDeleteView):
    model = Donation
    template_name = "events/donation_delete.html"
    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        event = self.object.event
        return reverse('events:event_detail', args=[event.id])

# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        #print("Add PK",pk)
        a = get_object_or_404(Event, id=pk)
        fav = Fav(user=request.user, event=a)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        #print("Delete PK",pk)
        a = get_object_or_404(Event, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, event=a).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()

def stream_file(request, pk):
    pic = get_object_or_404(Event, id=pk)
    response = HttpResponse()
    response['Content-Type'] = pic.content_type
    response['Content-Length'] = len(pic.picture)
    response.write(pic.picture)
    return response
