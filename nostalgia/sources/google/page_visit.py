from nostalgia.ndf import NDF
from nostalgia.sources.google import Google
from nostalgia.utils import datetime_from_format


def custom_parse(x):
    try:
        return datetime_from_format(x, "%Y-%m-%dT%H:%M:%SZ", in_utc=True)
    except:
        return datetime_from_format(x, "%Y-%m-%dT%H:%M:%S.%fZ", in_utc=True)


# class PageVisit(NDF):
#     @classmethod
#     def handle_dataframe_per_file(cls, data, file_path):
#         data["time"] = pd.to_datetime(data.time_usec, utc=True, unit="us").dt.tz_convert(tz)
#         del data["time_usec"]
#         return data

#     # refactor to use "google_takeout" as target
#     @classmethod
#     def load(
#         cls,
#         file_path="~/Downloads/Takeout_02-09-2018/Chrome/BrowserHistory.json",
#         nrows=None,
#         from_cache=True,
#         **kwargs
#     ):
#         page_visit = cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
#         if nrows is not None:
#             page_visit = page_visit.iloc[:5]
#         return cls(page_visit)


class PageVisit(Google, NDF):
    @classmethod
    def handle_dataframe_per_file(cls, data, file_path):
        data["time"] = [custom_parse(x) for x in data["time"]]
        return data

    # refactor to use "google_takeout" as target
    @classmethod
    def load(cls, takeout_folder, nrows=None, from_cache=True, **kwargs):
        if not takeout_folder.endswith("/"):
            takeout_folder += "/"
        file_path = takeout_folder + "My Activity/Chrome/My Activity.json"

        page_visit = cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
        if nrows is not None:
            page_visit = page_visit.iloc[:5]
        return cls(page_visit)
