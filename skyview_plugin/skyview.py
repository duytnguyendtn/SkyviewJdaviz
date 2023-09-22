from astroquery.skyview import SkyView
from traitlets import Dict, Bool, Unicode, Any, List

from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import PluginTemplateMixin, AddResultsMixin

__all__ = ['SkyviewPlugin']


@tray_registry('SkyviewPlugin', label="Skyview Plugin")
class SkyviewPlugin(PluginTemplateMixin, AddResultsMixin):
    """ Plugin to query Skyview and load data into Imviz """
    template_file = __file__, "skyview.vue"

    survey_collections = List().tag(sync=True)
    surveys = List().tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.survey_collections = list(SkyView.survey_dict.keys())
        self.collection_selected = None

        self.surveys = []
        self.survey_selected = None
    
    def vue_collection_selected(self, event):
        """Sync survey collection selected"""
        self.collection_selected = event
        if event is not None:
            self.surveys = SkyView.survey_dict[self.collection_selected]
    
    def vue_survey_selected(self, event):
        self.survey_selected = event

    def vue_submit_request(self, *args, **kwargs):
        print("Submitting Request...")
        files = SkyView.get_images(survey=self.survey_selected, position="14.5, 36.5")
        print(f"Files found: {files}")
        for file in files:
            self.app._jdaviz_helper.load_data(file)