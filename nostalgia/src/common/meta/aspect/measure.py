from nostalgia.src.common.meta.aspect import Aspect


class Measure(Aspect):
    def add_heartrate(self):
        return self.take_from("heartrate", "value")

    def heartrate_range(self, low, high=None):
        if "heartrate_value" not in self.columns:
            self.add_heartrate()
        if high is not None and low is not None:
            return self[(self["heartrate_value"] >= low) & self["heartrate_value"] < high]
        if low is not None:
            return self[self["heartrate_value"] >= low]
        if high is not None:
            return self[self["heartrate_value"] < high]

    def heartrate_above(self, value):
        return self.heartrate_range(value)

    def heartrate_below(self, value):
        return self.heartrate_range(None, value)
