from nostalgia.ndf import NDF


class Facebook(NDF):
    vendor = "facebook"
    ingest_settings = {
        "ingest_glob": "~/Downloads/facebook-*.zip",
        "recent_only": False,
        "delete_existing": True,
    }
