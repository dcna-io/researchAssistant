from django.shortcuts import render, redirect

# Create your views here.

from django.views import generic
from material import Layout, Fieldset, Row, Span2, Span5, Span7

from viewflow.decorators import flow_view
from viewflow.flow.views import StartFlowMixin, FlowMixin
from viewflow.flow.views.utils import get_next_task_url

from .forms import ResearchForm, BasesForm, SearchParamsForm, PaperReviewForm
from .models import ResearchProcess, Research, Paper


class StartView(StartFlowMixin, generic.UpdateView):
    form_class = ResearchForm

    layout = Layout(
        Row('name'),
        Row('objective')
        )

    def get_object(self):
        return self.activation.process.research

    def activation_done(self, form):
        research = form.save()
        self.activation.process.research = research 
        super(StartView, self).activation_done(form)

class BasesView(FlowMixin, generic.UpdateView):
    form_class = BasesForm

    def get_object(self):
        return self.activation.process.research

    def activation_done(self, form):
        research = form.save()
        self.activation.process.research = research 
        self.activation.done()

class SearchParams(FlowMixin, generic.UpdateView):
    form_class = SearchParamsForm

    def get_object(self):
        return self.activation.process.research

    def activation_done(self, form):
        research = form.save()
        self.activation.process.research = research 
        self.activation.done()


@flow_view
def paper_review(request, **kwargs):
    request.activation.prepare(request.POST or None, user=request.user)
    research = request.activation.process.research
    paper = research.papers.get(id=research.papers_metadata_analized)

    if request.method == "POST":
        form = PaperReviewForm(request.POST or None)
        if form.is_valid():
            approved = form.cleaned_data['approved']
            import ipdb; ipdb.set_trace()
            if not approved:
                research.papers.remove(paper)
            research.papers_metadata_analized += 1
            research.save()
            request.activation.done()
            return redirect(get_next_task_url(request, request.activation.process))
    else:
        form = PaperReviewForm()
    context = {
        'form': form,
        'activation': request.activation,
        'title': paper.title,
        'doi': paper.doi,
        'authors': paper.authors,
        'pubdate': paper.pubdate,
        'publication': paper.publication,
        'url': paper.url,
        'pages': paper.pages,
        'abstract': paper.abstract
    }
    return render(request, 'paper.html', context)