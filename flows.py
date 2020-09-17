import os
import logging
import sys
from viewflow import flow, frontend, lock
from viewflow.base import this, Flow
from viewflow.compat import _
from viewflow.flow import views as flow_views

from . import views
from .models import ResearchProcess
from .search_engines import acm, science_direct

logger = logging.getLogger(__name__)

@frontend.register
class ResearchFlow(Flow):
    process_class = ResearchProcess
    process_title = _("Research Assistant Process")
    process_description = _("This process helps researchers to find and analyze papers")

    lock_impl = lock.select_for_update_lock

    summary_template = ("Research: '{{ process.research.name }}'")

    start = (
        flow.Start(views.StartView)
        .Permission(auto_create=True)
        .Next(this.select_bases)
    )
    
    select_bases = (
        flow.View(views.BasesView)
        .Permission(auto_create=True)
        .Next(this.search_params)
    )

    search_params = (
        flow.View(views.SearchParams)
        .Permission(auto_create=True)
        .Next(this.approve)
    )

    approve = (
        flow.View(
            flow_views.UpdateProcessView, fields=['approved'],
            task_title=('Approve'),
            task_description=("Research {{ process.text }} approvement required"),
            task_result_summary=("Messsage was {{ process.approved }}")
        )
        .Permission(auto_create=True)
        .Next(this.check_approve)
    )

    check_approve = (
        flow.If(
            cond=lambda act: act.process.approved,
            task_title=_('Approvement check')
        )
        .Then(this.get_metadata)
        .Else(this.end)
    )

    get_metadata = (
        flow.Handler(
           this.get_papers_metadata,
           task_title="Getting papers metadata"
        )
        .Next(this.paper_review)
    )

    paper_review = (
        flow.View(views.paper_review)
        .Permission(auto_create=True)
        .Next(this.check_papers_for_review)
    )

    check_papers_for_review = (
        flow.If(
            cond=lambda act: len(act.process.research.papers.all()) == act.process.research.papers_metadata_analized,
            task_title=_('Approvement check'),
        )
        .Then(this.end)
        .Else(this.paper_review)
    )

    end = flow.End(
        task_title=_('End')
    )


    def get_papers_metadata(self, activation):
        #import ipdb; ipdb.set_trace()
        logger.info("Starting get metadata function")
        research = activation.process.research
        search_params = {
            'search_string': research.search_params_string,
            'date': research.search_params_date
        }
        papers = {}
        try:
          os.environ["SD_TOKEN"]
        except KeyError:
          print("Please set the environment variable SD_TOKEN as token for ScienceDirect API")
          sys.exit(1)
        token = os.environ["SD_TOKEN"]
        search_bases = research.search_bases.iterator()
        for base in search_bases:
            if base.name == "ACM Digital Library":
                logging.info("Getting ACM papers metadata")
                acm_search = acm.Acm()
                papers.update(acm_search.search(search_params))
            elif base.name == "ScienceDirect":
                logging.info("Getting ScienceDirect papers metadata")
                sd_search = science_direct.ScienceDirect(token)
                papers.update(sd_search.search(search_params))
        for doi in papers.keys():
            paper = papers[doi]
            paper.save()
            logging.info("Adding paper {}".format(paper.title))
            research.papers.add(paper)
