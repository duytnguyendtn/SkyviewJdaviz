from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import units as u
from pyvo.utils import vocabularies
from pyvo import registry
from traitlets import Dict, Bool, Unicode, Any, List, Int

from jdaviz.core.events import SnackbarMessage
from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import PluginTemplateMixin, AddResultsMixin

__all__ = ['PyVoPlugin']


@tray_registry('PyVoPlugin', label="PyVO Plugin")
class PyVoPlugin(PluginTemplateMixin, AddResultsMixin):
    """ Plugin to query PyVO and load data into Imviz """
    template_file = __file__, "pyvo.vue"

    wavebands = List().tag(sync=True)
    resources = List().tag(sync=True)

    source = Unicode().tag(sync=True)
    radius_deg = Int().tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.wavebands = [w.lower() for w in vocabularies.get_vocabulary("messenger")["terms"]]
        self.waveband_selected = None
        self._full_registry_results = None

        self.resources = []
        self.resource_selected = None

        self.radius_deg = 0


    def vue_waveband_selected(self,event):
        """Sync waveband selected"""
        self.waveband_selected = event
        if event is not None:
            self._full_registry_results = registry.search(registry.Servicetype("sia"), registry.Waveband(self.waveband_selected))
            self.resources = list(self._full_registry_results.getcolumn("short_name"))

    def vue_resource_selected(self, event):
        """Sync IVOA resource selected"""
        self.resource_selected = event


    def vue_submit_request(self, *args, **kwargs):
        try:
            sia_service = self._full_registry_results[self.resource_selected].get_service(service_type="sia")
            try:
                coord = SkyCoord(self.source)
            except:
                try:
                    coord = SkyCoord.from_name(self.source)
                except:
                    raise LookupError(f"Unable to resolve source coordinates: {self.source}")

            sia_results = sia_service.search(coord,
                                             size=((self.radius_deg * u.deg) if self.radius_deg > 0 else None),
                                             format='image/fits')
            if len(sia_results) == 0:
                raise RuntimeError("No observations returned")
            else:
                self.hub.broadcast(SnackbarMessage(
                    f"{len(sia_results)} SIA results found!", sender=self, color="success"))
        except Exception as e:
            self.hub.broadcast(SnackbarMessage(
                f"Unable to locate files for source {self.source}: {e}", sender=self, color="error"))
            raise

        print(f"SIA results found: {sia_results}")
        '''
        for file in files:
            self.app._jdaviz_helper.load_data(
                file,
                data_label=f"{self.source}_{self.survey_selected}")
        '''
        self.hub.broadcast(SnackbarMessage(
                    f"Loading data...", sender=self, color="success"))
        self.app._jdaviz_helper.load_data(
                fits.open(sia_results[0].getdataurl()),
                data_label=f"{self.source}_{self.survey_selected}")
        self.hub.broadcast(SnackbarMessage(
            #f"Successfully loaded {len(files)} Skyview product(s) for source {self.source}",
            f"Successfully loaded 1 Skyview product(s) for source {self.source}",
            sender=self,
            color="success"))
        
        
    def submit_pyvo_request(self):
        pass