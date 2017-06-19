# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta

import requests
import lxml
from pykml.factory import KML_ElementMaker as KML

URL = 'http://iss-positioner.nkoshelev.tech/lst'
NOW = datetime.utcnow()

PARAMS = dict(start_dt=NOW.isoformat(),
              end_dt=(NOW + timedelta(days=21)).isoformat(),
              dist='250',
              units='km',
              sun_angle=json.dumps({'$between': [1, 90]}))
FILES = dict(lst=open('uragan.lst', 'rb'))


def get_kml(data):
    kml = KML.kml(KML.Document(KML.open(1)))
    for dt, sessions in data.items():
        dt_fld = KML.Folder(KML.name(dt))
        for session in sessions:
            fld = KML.Folder(
                KML.name(session['title']),
                KML.Placemark(
                    KML.name('Traverse dt: {}, object: {}'.format(session['traverse']['dt'], session['title'])),
                    KML.Point(KML.coordinates("{longitude},{latitude},0".format(**session['traverse']['coord'])))
                ),
                KML.Placemark(
                    KML.name('Track - {title}'.format(**session)),
                    KML.LineString(
                        KML.coordinates(
                            '\n'.join(
                                "{longitude},{latitude},0".format(**coord['coord']) for coord in session['coords'])
                        )
                    )
                )
            )

            dt_fld.append(fld)
        kml.Document.append(dt_fld)

    kml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + lxml.etree.tostring(kml, pretty_print=True).decode()
    return kml_str


def main():
    start = datetime.utcnow()
    resp = requests.post(URL, data=PARAMS, files=FILES)
    result = resp.json()
    print(datetime.utcnow() - start)

    if result['error']:
        return
    kml = get_kml(result['data'])
    with open('example.kml', 'w') as f:
        f.write(kml)


if __name__ == '__main__':
    main()
