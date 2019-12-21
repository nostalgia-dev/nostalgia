from nostalgia.ndf import NDF


class Google(NDF):
    vendor = "google"
    ingest_settings = {
        "ingest_glob": "~/Downloads/takeout-20*-*.zip",
        "recent_only": False,
        "delete_existing": False,
    }
