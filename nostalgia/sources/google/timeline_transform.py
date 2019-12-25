# <Placemark>
#   <name>Home (Laan van Henegouwen 16)</name>
#   <address>3703 TD Zeist</address>
#   <ExtendedData>
#     <Data name="Email">
#       <value>kootenpv@gmail.com</value>
#     </Data>
#     <Data name="Category">
#       <value/>
#     </Data>
#     <Data name="Distance">
#       <value>0</value>
#     </Data>
#   </ExtendedData>
#   <description>  from 2019-01-04T16:41:11.016Z to 2019-01-05T16:29:16.926Z. Distance 0m </description>
#   <Point>
#     <coordinates>5.2261821,52.080966499999995,0</coordinates>
#   </Point>
#   <TimeSpan>
#     <begin>2019-01-04T16:41:11.016Z</begin>
#     <end>2019-01-05T16:29:16.926Z</end>
#   </TimeSpan>
# </Placemark>

import pandas as pd
import lxml.etree
from dateutil.parser import parse as date_parse
import just
from nostalgia.times import yesterday
from nostalgia.utils import format_latlng

N = {"klm": "http://www.opengis.net/kml/2.2"}

# cats = set()
days = []
for fname in sorted(just.glob("/home/pascal/Downloads/ghistory/history-*.kml")):
    # for fname in sorted(["/home/pascal/Downloads/ghistory/history-2018-07-25.kml"]):
    tree = lxml.etree.parse(fname)
    for placemark in tree.xpath("//klm:Placemark", namespaces=N):
        name = placemark.xpath("./klm:name/text()", namespaces=N)[0]
        address = placemark.xpath("./klm:address/text()", namespaces=N)
        address = address[0] if address else None
        start = date_parse(placemark.xpath("./klm:TimeSpan/klm:begin/text()", namespaces=N)[0])
        end = date_parse(placemark.xpath("./klm:TimeSpan/klm:end/text()", namespaces=N)[0])
        category = placemark.xpath(
            "./klm:ExtendedData/klm:Data[@name='Category']/klm:value/text()", namespaces=N
        )
        category = category[0] if category else None
        # just a location
        if category is None and address is None:
            continue
        if category is None and " (" in name:
            category = name.split(" (")[0]
        if "Steynlaan" in name:
            category = "Home"
        distance = placemark.xpath(
            "./klm:ExtendedData/klm:Data[@name='Distance']/klm:value/text()", namespaces=N
        )
        distance = distance[0] if distance else None
        # fuckers, lon|lat instead of lat|lon
        coords = placemark.xpath("./klm:Point/klm:coordinates/text()", namespaces=N)
        coords = coords or placemark.xpath("./klm:LineString/klm:coordinates/text()", namespaces=N)
        d = {
            "date": start.date(),
            "name": name,
            "distance": distance,
            "category": category,
            "start": start,
            "end": end,
            "address": address,
            "month": start.month,
            "hour": start.hour,
            "year": start.year,
        }
        loc = {"lat": None, "lon": None, "coordinates": []}
        # here switch lon|lat
        coor = sum(
            [
                [format_latlng((x.split(",")[1], x.split(",")[0])).split(", ") for x in c.split()]
                for c in coords
            ],
            [],
        )
        if coor:
            loc["coordinates"] = coor
            loc["lat"] = coor[0][0]
            loc["lon"] = coor[0][1]
        # for data in placemark.xpath("//klm:Data", namespaces=N):
        #     cats.update(data.xpath("./@name", namespaces=N))
        d.update(loc)
        days.append(d)

df = pd.DataFrame(days)
df = df.reindex(list(d.keys()), axis=1)


yday = yesterday()
tmpl = "/home/pascal/Downloads/timeline_data-{}-{:02d}-{:02d}.csv"
df.to_csv(tmpl.format(yday.year, yday.month, yday.day))
