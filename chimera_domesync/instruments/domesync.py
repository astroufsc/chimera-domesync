from chimera.instruments.dome import DomeBase

# If dome uses .features() one implementation could be:
# http://stackoverflow.com/questions/21060073/dynamic-inheritance-in-python
#
from chimera_domesync.util.dome_track import AzimuthModel


class DomeSync(DomeBase):
    __config__ = {
        'device': "Virtual",
        'dome': None,
        'site': '/Site/0',
        'telescope': '/Telescope/0',
        'az_resolution': None,
        "dome_radius": 147,
        "mount_dec_height": 0,
        "mount_dec_length": 49.2,
        "mount_dec_offset": 0,
    }

    def __start__(self):
        self.setHz(1.0 / 30.0)
        self._DomeModel = AzimuthModel(self._getSite()['latitude'], self['dome_radius'], self['mount_dec_height'],
                                       self['mount_dec_length'], self['mount_dec_offset'])
        print 'latitude', self._getSite()['latitude'].R

    def _getSite(self):
        return self.getManager().getProxy(self["site"], lazy=True)

    def _getDome(self):
        dome = self.getManager().getProxy(self["dome"], lazy=True)
        if self["az_resolution"] is None:
            self["az_resolution"] = dome["az_resolution"]
        return self.getManager().getProxy(self["dome"], lazy=True)

    def _getTelescope(self):
        return self.getManager().getProxy(self["telescope"], lazy=True)

    def _getDomeAz(self, az):
        return self._DomeModel.solve_dome_azimuth(self._getTelescope().getPositionRaDec(),
                                                  lst=self._getSite().LST_inRads())

    def _getDomeAzSynced(self, dome_az):
        az = dome_az  # TODO:
        return az

    def slewToAz(self, az):
        return self._getDome().slewToAz(self._getDomeAz(az))

    def isSlewing(self):
        return self._getDome().isSlewing()

    def abortSlew(self):
        return self.abortSlew()

    def getAz(self):
        return self._getDomeAzSynced(self._getDome().getAz())

    def openSlit(self):
        return self._getDome().openSlit()

    def closeSlit(self):
        return self._getDome().closeSlit()

    def isSlitOpen(self):
        return self._getDome().isSlitOpen()

    def openFlap(self):
        return self._getDome().openFlap()

    def closeFlap(self):
        return self._getDome().closeFlap()

    def isFlapOpen(self):
        return self._getDome().isFlapOpen()

    def getMetadata(self, request):
        return self._getDome().getMetadata()
