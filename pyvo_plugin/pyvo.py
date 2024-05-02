from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import units as u
from pyvo.utils import vocabularies
from pyvo import registry
from traitlets import Dict, Bool, Unicode, Any, List, Int

from jdaviz.core.events import SnackbarMessage
from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import PluginTemplateMixin, AddResultsMixin, TableMixin

__all__ = ['PyVoPlugin']


@tray_registry('PyVoPlugin', label="PyVO Plugin")
class PyVoPlugin(PluginTemplateMixin, AddResultsMixin, TableMixin):
    """ Plugin to query PyVO and load data into Imviz """
    template_file = __file__, "pyvo.vue"

    wavebands = List().tag(sync=True)
    resources = List([]).tag(sync=True)
    resources_loading = Bool(False).tag(sync=True)

    source = Unicode().tag(sync=True)
    radius_deg = Int(1).tag(sync=True)

    results_loading = Bool(False).tag(sync=True)
    data_loading = Bool(False).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Waveband properties to filter available registry resources
        self.wavebands = [w.lower() for w in vocabularies.get_vocabulary("messenger")["terms"]]
        self.waveband_selected = None

        self._full_registry_results = None
        self.resource_selected = None

        self.table.headers_avail = ["Title", "Instrument", "DateObs", "URL"]
        self.table.headers_visible = ["Title", "Instrument", "DateObs"]

        self.table.show_select = True
        self.table.item_key = "URL"
        self.table.add_item({"URL": "TestURL", "Instrument": "TestDet", "Title": "Test"})


    def vue_waveband_selected(self,event):
        """Sync waveband selected"""
        self.waveband_selected = event
        # Clear existing resources list
        self.resources = []
        self.resource_selected = None
        self.resources_loading = True
        try:
            if event is not None:
                self._full_registry_results = registry.search(registry.Servicetype("sia"), registry.Waveband(self.waveband_selected))
                self.resources = list(self._full_registry_results.getcolumn("short_name"))
        except Exception:
            # TODO: Catch connection error
            raise
        finally:
            self.resources_loading = False

    def vue_resource_selected(self, event):
        """Sync IVOA resource selected"""
        self.resource_selected = event


    def vue_query_resource(self, *args, **kwargs):
        self.table.items = []
        self.results_loading = True
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
        finally:
            self.results_loading = False

        print(f"SIA results found: {sia_results}")
        try:
            for result in sia_results:
                self.table.add_item({"Title": str(result.title), "URL": str(result.getdataurl()), "Instrument": str(result.instr), "DateObs": str(result.dateobs)})
            self.hub.broadcast(SnackbarMessage(
                    f"{len(sia_results)} SIA results populated!", sender=self, color="success"))
        except Exception as e:
            self.hub.broadcast(SnackbarMessage(
                f"Unable to populate table for source {self.source}: {e}", sender=self, color="error"))
            raise


    def vue_load_selected_data(self,event):
        self.data_loading = True
        for entry in self.table.selected_results:
            try:
                self.app._jdaviz_helper.load_data(
                    fits.open(str(entry["URL"])),
                    data_label=f"{self.source}_{self.resource_selected}_{entry['Title']}")
            except Exception as e:
                self.hub.broadcast(SnackbarMessage(
                    f"Unable to load file to viewer: {entry['URL']}: {e}", sender=self, color="error"))
        self.data_loading = False
        self.table.selected_results = []
        
    def submit_pyvo_request(self):
        pass