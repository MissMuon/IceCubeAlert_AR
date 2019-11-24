class Event:
    def __init__(self, alert_type=None, signal_prob=None, far=None, e_mu=None, e_nu=None, ra=None, dec=None,
                 angle_err_50=None, angle_err_90=None, run=None, event_id=None, event_time=None, mjd=None,
                 rec_x=None, rec_y=None, rec_z=None, rec_t0=None, zen_rad=None, azi_rad=None,
                 ra_rad=None, dec_rad=None):
        self.alert_type = alert_type
        self.signal_prob = signal_prob
        self.far = far
        self.e_mu = e_mu
        self.e_nu = e_nu
        self.ra = ra
        self.dec = dec
        self.angle_err_50 = angle_err_50
        self.angle_err_90 = angle_err_90
        self.run = run
        self.id = event_id
        self.time = event_time
        self.mjd = mjd
        self.rec_x = rec_x
        self.rec_y = rec_y
        self.rec_z = rec_z
        self.rec_t0 = rec_t0
        self.zen_rad = zen_rad
        self.azi_rad = azi_rad
        self.ra_rad = ra_rad
        self.dec_rad = dec_rad

    def set_track_info(self, mjd, rec_x, rec_y, rec_z, rec_t0, zen_rad, azi_rad, ra_rad, dec_rad):
        self.mjd = mjd
        self.rec_x = rec_x
        self.rec_y = rec_y
        self.rec_z = rec_z
        self.rec_t0 = rec_t0
        self.zen_rad = zen_rad
        self.azi_rad = azi_rad
        self.ra_rad = ra_rad
        self.dec_rad = dec_rad

    def __str__(self):
        return f"Event/Run {self.id, self.run} E_nu={self.e_nu} RA/DEC={self.ra}/{self.dec} @{self.time}"

    @property
    def props(self):
        return [self.alert_type, self.signal_prob, self.far, self.e_mu, self.e_nu, self.ra, self.dec,
                self.angle_err_50, self.angle_err_90, self.run, self.id, self.time,
                self.mjd, self.rec_x, self.rec_y, self.rec_z, self.rec_t0, self.zen_rad,
                self.azi_rad, self.ra_rad, self.dec_rad]

    propnames = ["alert_type", "signal_prob", "far", "e_mu", "e_nu", "ra", "dec",
                 "angle_err_50", "angle_err_90", "run", "event", "event_time",
                 "mjd", "rec_x", "rec_y", "rec_z", "rec_t0", "zen_rad", "azi_rad", "ra_rad", "dec_rad"]

    @classmethod
    def propsstr(cls):
        return ("{}," * len(cls.propnames)).format(*cls.propnames)[:-1]
