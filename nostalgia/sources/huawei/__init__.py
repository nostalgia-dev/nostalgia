from nostalgia.ndf import NDF
import just
import os


class Huawei(NDF):
    vendor = "huawei"
    ingest_settings = {
        "ingest_glob": "~/Downloads/HUAWEI_HEALTH_*.zip",
        "recent_only": True,
        "delete_existing": True,
    }

    @classmethod
    def ingest(cls, password, *args, **kwargs):
        fname = just.glob(cls.ingest_settings["ingest_glob"])[-1]
        os.system(f"7z x -y -p'{password}' {fname}")
        just.rename(
            "~/Downloads/Health detail data & description/health detail data.json",
            "~/nostalgia_data/input/huawei/health_detail_data.json",
            no_exist=True,
        )
        print("----\ndata rows ingested:", len(just.read("~/nostalgia_data/input/huawei/health_detail_data.json")))

    @classmethod
    def yield_rows(cls, key, nrows=None):
        data = just.read("~/nostalgia_data/input/huawei/health_detail_data.json")
        count = 0
        for x in data:
            for row in x["samplePoints"]:
                if key not in row["key"]:
                    continue
                yield row
                count += 1
            if nrows is not None and count > nrows:
                break


class Heartrate(Huawei):
    @classmethod
    def load(cls, nrows=None):
        return cls(
            [
                {
                    "start": datetime_from_timestamp(row["startTime"]),
                    "end": datetime_from_timestamp(row["endTime"]),
                    "value": row["value"],
                }
                for row in cls.yield_rows("HEARTRATE", nrows)
            ]
        )
