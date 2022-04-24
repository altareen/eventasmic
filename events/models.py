from datetime import date
from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from django.conf import settings
from taggit.managers import TaggableManager

# Create your models here.

class Event(models.Model) :
    performer = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Performer must be greater than 2 characters")]
    )
    pledge = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    showdate = models.DateField(validators=[MinValueValidator(limit_value=date.today)], null=True)
    #showtime = models.TimeField(null=True)
    showtime = models.CharField(max_length=200, null=True)
    venue = models.CharField(max_length=200, null=True)
    text = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Picture
    picture = models.BinaryField(null=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Favorites
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Fav', related_name='favorite_events')

    # Tags
    # https://django-taggit.readthedocs.io/en/latest/api.html#TaggableManager
    tags = TaggableManager(blank=True)
    
    # Shows up in the admin list
    def __str__(self):
        return self.performer

class Comment(models.Model) :
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15:
            return self.text
        return self.text[:11] + ' ...'

class Donation(models.Model) :
    amount = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Fav(models.Model) :
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # https://docs.djangoproject.com/en/3.2/ref/models/options/#unique-together
    class Meta:
        unique_together = ('event', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.event.title[:10])
