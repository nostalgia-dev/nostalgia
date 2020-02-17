from nostalgia.ndf import NDF


class Apple(NDF):
    vendor = "apple"
    ingest_settings = {
        "ingest_glob": "~/Downloads/apple/*.zip",
        "recent_only": False,
        "delete_existing": False,
    }

if __name__ == "__main__":
    Apple.ingest()