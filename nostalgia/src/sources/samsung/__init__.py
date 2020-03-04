from nostalgia.ndf import NDF


class Samsung(NDF):
    vendor = "samsung"
    ingest_settings = {
        "ingest_glob": "~/Downloads/samsunghealth_*.zip",
        "recent_only": True,
        "delete_existing": True,
    }
