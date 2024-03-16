from lxml import etree
import pandas as pd

def generate_coordinates(gpx_file, gpx_destination):
    # Parse the XML file
    tree = etree.parse(gpx_file)
    root = tree.getroot()

    # GPX namespace
    ns = {'default': 'http://www.topografix.com/GPX/1/1'}

    # Extracting data
    data = []
    for trkpt in root.findall('.//default:trkpt', ns):
        lat = trkpt.get('lat')
        lon = trkpt.get('lon')
        time_element = trkpt.find('default:time', ns)
        time = time_element.text if time_element is not None else None
        data.append({'Timestamp': time, 'lat': [lat,lon]})

    # Create DataFrame
    gpx_coordinates = pd.DataFrame(data)
    gpx_coordinates['Coordinates'] = gpx_coordinates['Coordinates'].apply(lambda x: [float(i) for i in x])
    gpx_coordinates.to_csv(gpx_destination, index=False)
