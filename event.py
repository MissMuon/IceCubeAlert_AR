class Event:
    def __init__(self, alert_type=None, signal_prob=None, far=None, e_mu=None, e_nu=None, ra=None, dec=None,
                 angle_err_50=None, angle_err_90=None, run=None, event_id=None, event_time=None):
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

    def __str__(self):
        return f"Event/Run {self.id, self.run} E_nu={self.e_nu} RA/DEC={self.ra}/{self.dec} @{self.time}"

    @property
    def props(self):
        return [self.alert_type, self.signal_prob, self.far, self.e_mu, self.e_nu, self.ra, self.dec,
                self.angle_err_50, self.angle_err_90, self.run, self.id, self.time]

    propnames = ["alert_type", "signal_prob", "far", "e_mu", "e_nu", "ra", "dec",
                 "angle_err_50", "angle_err_90", "run", "event", "event_time"]

    @classmethod
    def propsstr(cls):
        return ("{}," * len(cls.propnames)).format(*cls.propnames)[:-1]
