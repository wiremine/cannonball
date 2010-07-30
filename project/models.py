from django.db import models
from django.utils.translation import ugettext_lazy as _
#from django.contrib.contenttypes.models import ContentType
#from django.contrib.contenttypes import generic
#from tinymce import models as tinymce_models
#from filebrowser.fields import FileBrowseField

class Project(models.Model):
    """
    Represents a single git-based project.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    path_to_repo = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['name']


#class ProjectNotification(models.Model):
#    """
#    People who get notified about a project
#    """
#    project = models.ForeignKey(Project)
#    name = models.CharField(blank=True, max_length=100)
#    email = models.EmailField()
#    active = models.BooleanField(default=True)
#    

#    def __unicode__(self):
#        return self.email

#    class Meta:
#        verbose_name = 'Project Notification'
#        verbose_name_plural = 'Project Notifications'
#        ordering = ['email']



        