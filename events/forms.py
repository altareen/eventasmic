import datetime
from django import forms
from events.models import Event
from django.core.files.uploadedfile import InMemoryUploadedFile
from events.humanize import naturalsize

# Create the form class.
class CreateForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    # Call this 'picture' so it gets copied from the form to the in-memory model
    # It will not be the "bytes", it will be the "InMemoryUploadedFile"
    # because we need to pull out things like content_type
    picture = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'picture'
    #showdate = forms.DateField(initial=datetime.date.today, widget = forms.SelectDateWidget())
    #TIMES = (('12:00PM', '12:00PM'), ('1:00PM', '1:00PM'), ('2:00PM', '2:00PM'), ('3:00PM', '3:00PM'), ('4:00PM', '4:00PM'), ('5:00PM', '5:00PM'), ('6:00PM', '6:00PM'), ('7:00PM', '7:00PM'), ('8:00PM', '8:00PM'),)
    #showtime = forms.ChoiceField(choices=TIMES)
    CHOICES = (('Babeville','Babeville'), ('Town Ballroom','Town Ballroom'), ('Tralf Music Hall','Tralf Music Hall'), ('Iron Works','Iron Works'), ('The Icon','The Icon'), ('Mohawk Place','Mohawk Place'), ('The Cave','The Cave'), ('Rec Room','Rec Room'), ('Riviera Theater','Riviera Theater'), ('Keybank Center','Keybank Center'),)
    venue = forms.ChoiceField(choices=CHOICES)

    # Hint: this will need to be changed for use in the ads application :)
    class Meta:
        model = Event
        fields = ['performer', 'pledge', 'venue', 'text', 'tags', 'picture']
        #fields = ['performer', 'pledge', 'showdate', 'showtime', 'venue', 'text', 'tags', 'picture']  # Picture is manual

    # Validate the size of the picture
    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('picture')
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error('picture', "File must be < "+self.max_upload_limit_text+" bytes")
            
    # Convert uploaded File object to a picture
    def save(self, commit=True):
        instance = super(CreateForm, self).save(commit=False)

        # We only need to adjust picture if it is a freshly uploaded file
        f = instance.picture   # Make a copy
        if isinstance(f, InMemoryUploadedFile):  # Extract data from the form to the model
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.picture = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()
            self.save_m2m()

        return instance

# strip means to remove whitespace from the beginning and the end before storing the column
class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)

class DonationForm(forms.Form):
    #donation = forms.DecimalField(max_digits=7, decimal_places=2)
    donation = forms.ChoiceField(choices=[(1.0*x, 1.0*x) for x in range(25, 500, 25)])

# https://docs.djangoproject.com/en/3.0/topics/http/file-uploads/
# https://stackoverflow.com/questions/2472422/django-file-upload-size-limit
# https://stackoverflow.com/questions/32007311/how-to-change-data-in-django-modelform
# https://docs.djangoproject.com/en/3.0/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
