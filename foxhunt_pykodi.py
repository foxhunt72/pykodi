#
import requests
import json
import operator






class foxhunt_pykodi:
    """Dit is een class

    usage: ....

    """

    def __init__(self, kodi_url,debug=False):
        self.url = kodi_url
        self.debug = debug
        self.session = requests.session()

    def print(self, text):
        """internal print only if debug is true, used internally"""
        if self.debug == True:
            print(text)
 
    def get_json(self,json_request):
        """ internal get json """
        r = self.session.post(self.url,data=json_request)
        return(r.json())

    def get_series(self):
        """ get series """
        json_request='{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "filter": {"field": "playcount", "operator": "is", "value": "0"}, "properties": ["art", "genre", "plot", "title", "originaltitle", "year", "rating", "thumbnail", "playcount", "file", "fanart"], "sort": { "order": "ascending", "method": "label" } }, "id": "libTvShows"}' 
        output=self.get_json(json_request)['result']['tvshows']
        return(output)


    def get_episodes(self,tvshow,sort=False):
        """ get episoded """
        json_request="""   {
                                "id": 70,
                                "jsonrpc": "2.0",
                                "method": "VideoLibrary.GetEpisodes",
                                "params": {
                                    "tvshowid": %d,
                                    "limits": {
                                        "end": 500,
                                        "start": 0
                                    },
                                    "properties": [
                                        "episode",
                                        "season",
                                        "firstaired",
                                        "rating",
                                        "plot",
                                        "title",
                                        "originaltitle",
                                        "playcount",
                                        "showtitle",
                                        "tvshowid",
                                        "dateadded",
                                        "file",
                                        "resume",
                                        "streamdetails",
                                        "specialsortepisode",
                                        "specialsortseason",
                                        "lastplayed",
                                        "art",
                                        "userrating"
                                    ]
                                }
                            } """
        output=self.get_json(json_request % (tvshow))['result']['episodes']
        if sort == True:
            output.sort(key=operator.itemgetter('episode'))
            output.sort(key=operator.itemgetter('season'))
        return(output)

