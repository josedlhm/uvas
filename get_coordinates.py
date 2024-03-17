from lxml import etree
import pandas as pd
import ast

def generate_coordinates(gpx_file, gpx_destination):
    # Parse the XML file
    tree = etree.parse(gpx_file)
    root = tree.getroot()

    # GPX namespace
    ns = {'default': 'http://www.topografix.com/GPX/1/1'}

    # Extracting data
    data = []
    for trkpt in root.findall('.//default:trkpt', ns):
        lat = float(trkpt.get('lat'))
        lon = float(trkpt.get('lon'))
        time_element = trkpt.find('default:time', ns)
        time = time_element.text if time_element is not None else None
        data.append({'Timestamp': time, 'Coordinates': [lat,lon]})

    # Create DataFrame
    gpx_coordinates = pd.DataFrame(data)
    gpx_coordinates.to_csv(gpx_destination, index=False)