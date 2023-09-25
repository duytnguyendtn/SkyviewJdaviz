from astropy import units as u
from astroquery.skyview import SkyView
from traitlets import Dict, Bool, Unicode, Any, List, Int

from jdaviz.core.events import SnackbarMessage
from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import PluginTemplateMixin, AddResultsMixin

__all__ = ['SkyviewPlugin']


@tray_registry('SkyviewPlugin', label="Skyview Plugin")
class SkyviewPlugin(PluginTemplateMixin, AddResultsMixin):
    """ Plugin to query Skyview and load data into Imviz """
    template_file = __file__, "skyview.vue"

    survey_collections = List().tag(sync=True)
    surveys = List().tag(sync=True)
    source = Unicode().tag(sync=True)
    resolution_pix = Int().tag(sync=True)
    radius_deg = Int().tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.survey_collections = list(SkyView.survey_dict.keys())
        self.collection_selected = None

        self.surveys = []
        self.survey_selected = None

        self.resolution_pix = 300
        self.radius_deg = 0
    
    def vue_collection_selected(self, event):
        """Sync survey collection selected"""
        self.collection_selected = event
        if event is not None:
            self.surveys = SkyView.survey_dict[self.collection_selected]
    
    def vue_survey_selected(self, event):
        self.survey_selected = event

    def vue_submit_request(self, *args, **kwargs):
        try:
            files = SkyView.get_images(survey=self.survey_selected,
                        position=self.source,
                        pixels=self.resolution_pix,
                        radius=((self.radius_deg * u.deg) if self.radius_deg > 0 else None))
            if files == []:
                raise RuntimeError("No files returned")
            else:
                self.hub.broadcast(SnackbarMessage(
                    f"Files Found!", sender=self, color="success"))
        except Exception as e:
            self.hub.broadcast(SnackbarMessage(
                f"Unable to locate files for source {self.source}: {e}", sender=self, color="error"))
            raise

        print(f"Files found: {files}")
        for file in files:
            self.app._jdaviz_helper.load_data(
                file,
                data_label=f"{self.source}_{self.survey_selected}")
        self.hub.broadcast(SnackbarMessage(
            f"Successfully loaded {len(files)} Skyview product(s) for source {self.source}",
            sender=self,
            color="success"))