from django.db import models
from viewflow.models import Process
from viewflow.compat import _

# Create your models here.

class SearchBases(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Paper(models.Model):

    doi = models.CharField(max_length=50)
    authors = models.CharField(max_length=200)
    pubdate = models.CharField(max_length=30, null=True)
    title = models.CharField(max_length=200)
    publication = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    pages = models.CharField(max_length=10, null=True)
    abstract = models.TextField()

    class Meta:
        ordering = ['doi']

    def __str__(self):
        return self.title


class Research(models.Model):
    years = [tuple([x,x]) for x in range(2020,2000, -1)]

    name = models.CharField(max_length=200)
    objective = models.TextField()
    search_bases = models.ManyToManyField(SearchBases) 
    search_params_string = models.CharField(max_length=300, null=True, help_text="Search string")
    search_params_date = models.IntegerField(choices=years, null=True, help_text="After year")
    papers = models.ManyToManyField(Paper)
    papers_metadata_analized = models.IntegerField(default=1)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ResearchProcess(Process):
    research = models.ForeignKey(Research, blank=True, null=True, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
