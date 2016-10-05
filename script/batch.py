from __future__ import print_function

import os

from script.catalog import Catalog
from script.export import area_json_output, area_csv_output
from script.parser import Area, restore_area


def batch_parser(codes, area_type=1, media_path="", with_log=False, catalog="", coord_out="EPSG:3857",
                 output=os.path.join("output")):
    catalog = Catalog(catalog)
    areas = []
    restores = []
    with_error = 0
    success = 0
    from_catalog = 0
    print("Launched parsing of %i areas:" % len(codes))
    print("================================")
    for c in codes:
        code = c.strip()
        print("%s" % code, end="")
        restore = catalog.find(code)
        area = None
        if not restore:
            try:
                area = Area(code, media_path=media_path, area_type=area_type, with_log=with_log, coord_out=coord_out)
                restore = catalog.update(area)
                print(" - ok")
                success += 1
            except Exception as er:
                print(" - error")
                with_error += 1
                pass
        else:
            print(" - ok, from catalog")
            success += 1
            from_catalog += 1
            area = restore_area(restore, coord_out)
        restores.append(restore)

        if area:
            areas.append(area)
            area_json_output(output, area)
            area_csv_output(output, area)

    catalog.close()

    print("=================")
    print("Parsing complate:")
    print("  success     : %i" % success)
    print("  error       : %i" % with_error)
    print("  from catalog: %i" % from_catalog)
    print("-----------------")

