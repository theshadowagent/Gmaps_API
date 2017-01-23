import googlemaps
import requests

API_KEY = ''  # TODO: Replace this with your API_KEY


class GMapsAPIRequest(object):
    language = 'ru'  # Default language https://developers.google.com/maps/faq#languagesupport
    region = 'ru'  # https://developers.google.com/maps/documentation/geocoding/intro#RegionCodes

    def __init__(self, language=language, region=region):
        self.maps = googlemaps.Client(key=API_KEY)


class GMapsAPIResponse(object):
    # self.answer is a response dictionary

    def __init__(self, answer):
        self.answer = answer


class Location(dict):
    def __init__(self, dict):
        super(Location, self).__init__()
        self['latitude'] = dict['lat']
        self['longitude'] = dict['lng']


class ViewPort(dict):  # recommended bounds of MapView in your application
    def __init__(self, data):
        super(ViewPort, self).__init__()
        self['northeast'] = Location(data['northeast'])  # northeast corner coordinate
        self['southwest'] = Location(data['southwest'])  # southwest corner coordinate


class GMapsGeocodeResult(GMapsAPIResponse):

    # self.location is an object of class Location, which is {'latitude': ..., 'longitude': ...}
    # self.viewPort is a {'northeast' : {'latitude': ..., 'longitude': ...}, '
    # self.formattedAddress is an address string
    # self.locationType is a string, which defines location accuracy
    # self.answer is a response dictionary

    def __init__(self, answer):
        super(GMapsGeocodeResult, self).__init__(answer)
        geometry = answer['geometry']
        self.location = Location(geometry['location'])
        self.viewPort = ViewPort(geometry['viewport'])
        self.locationType = geometry['location_type']
        self.formattedAddress = answer['formatted_address']


class GMapsGeocodeRequest(GMapsAPIRequest):
    # https://developers.google.com/maps/documentation/geocoding/intro#geocoding
    locationType = "ROOFTOP" # default location type

    def __init__(self, language=GMapsAPIRequest.language, region=GMapsAPIRequest.region, location_type=locationType):
        super(GMapsGeocodeRequest, self).__init__()
        self.language = language
        self.region = region
        self.locationType = location_type

    def get_address(self, latitude, longitude):  # returns list of GMapsGeocodeResult
        answer = self.maps.reverse_geocode((latitude, longitude), language=self.language,
                                                            location_type=self.locationType)
        answer = list(map(GMapsGeocodeResult, answer))
        return answer

    def get_location_from_address(self, address):  # returns list of GMapsGeocodeResult
        answer = self.maps.geocode(address, language=self.language, region=self.region)
        answer = list(map(GMapsGeocodeResult, answer))
        return answer


class GMapsGeolocationResult(GMapsAPIResponse):
    def __init__(self, answer):

        super(GMapsGeolocationResult, self).__init__(answer)
        self.location = Location(answer['location'])
        self.accuracy = answer['accuracy']


class GMapsGeolocationRequest(GMapsAPIRequest):
    REQUEST_URL = 'https://www.googleapis.com/geolocation/v1/geolocate'

    def get_current_location(self):
        session = requests.Session()
        response = session.post(self.REQUEST_URL, params={'key':API_KEY}).json()
        return GMapsGeolocationResult(response)


class GMapsDistanceMatrixResult(GMapsAPIResponse):
    def __init__(self, answer):
        super(GMapsDistanceMatrixResult, self).__init__(answer)
        self.destinationAddresses = answer['destination_addresses']
        self.originAddresses = answer['origin_addresses']
        durations = {}
        distances = {}
        rows = answer['rows']
        i = 0
        for destination in self.destinationAddresses:
            j = i
            for origin in self.originAddresses:
                element = rows[i]['elements'][j]
                durations[(origin, destination)] = element['duration']
                distances[(origin, destination)] = element['distance']
                j += 1
            i += 1
        self.distances = distances
        self.durations = durations


class GMapsDistanceMatrixRequest(GMapsAPIRequest):
    defaultTransitMode = ['subway', 'bus']
    defaultMode = 'driving'

    def __init__(self, language=GMapsAPIRequest.language, default_mode=defaultMode, default_transit_mode=defaultTransitMode):
        super(GMapsDistanceMatrixRequest, self).__init__()
        self.language = language
        self.defaultTransitMode = default_transit_mode
        self.defaultMode = default_mode

    def get_distance_time(self, origin_addresses, destination_addresses, event_time=None, mode=defaultMode,
                          transit_mode=defaultTransitMode):
        # mode: driving, walking, bicycling, transit (public transport)
        if mode != "transit":
            transit_mode = None
        return GMapsDistanceMatrixResult(self.maps.distance_matrix(origin_addresses, destination_addresses,
                                                                   arrival_time=event_time,
                                                                   mode=mode, transit_mode=transit_mode,
                                                                   language=self.language))


# Direction answer isn't parsed
class GMapsDirectionRequest(GMapsAPIRequest):
    defaultTransitMode = ['subway', 'bus']
    defaultMode = 'driving'

    def __init__(self, language=GMapsAPIRequest.language, region=GMapsAPIRequest.region, default_mode=defaultMode, default_transit_mode=defaultTransitMode):
        super(GMapsDirectionRequest, self).__init__()
        self.language = language
        self.region = region
        self.defaultTransitMode = default_transit_mode
        self.defaultMode = default_mode
        self.alternatives = False

    def get_directions(self, origin, destination, event_time=None, mode=defaultMode,
                       transit_mode=defaultTransitMode):
        # mode: driving, walking, bicycling, transit (public transport)
        if mode != "transit":
            transit_mode = None
        return self.maps.directions(origin, destination,
                                    arrival_time=event_time,
                                    mode=mode, transit_mode=transit_mode,
                                    language=self.language,
                                    alternatives=self.alternatives)


class GMapsStaticMapsRequest(GMapsAPIRequest):
    REQUEST_URL = 'https://maps.googleapis.com/maps/api/staticmap'

    def __init__(self, language=GMapsAPIRequest.language):
        self.language = language

    def get_map_snapshot_url(self, address):
        params = {'markers': 'color:red|size:small|'+address, 'size':'500x300'}
        request = requests.Request('GET', self.REQUEST_URL, params=params).prepare()
        return request.url

    def get_map_snapshot_url_from_location(self, coordinate_dict):
        params = {'markers': 'color:red|size:small|'+str(coordinate_dict['latitude'])+','+str(coordinate_dict['longitude']),
                  'size':'500x300'}
        request = requests.Request('GET', self.REQUEST_URL, params=params).prepare()
        return request.url

# Example request
# TODO: Replace this with your request
# if __name__ == "__main__":
    # gmaps = GMapsGeocodeRequest()
    # print(gmaps.get_location_from_address(u"Одинцово, Чистяковой 22")[0].location['latitude'])
    # print(GMapsStaticMapsRequest().get_map_snapshot_url(u"Москва, Кочновский проезд 20"))
