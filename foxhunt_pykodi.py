#
import requests
import json
import operator






class foxhunt_pykodi:
    """Dit is een class

    usage: ....

    """

    def __init__(self, kodi_url, debug=False):
        self.url = kodi_url
        self.debug = debug
        self.session = requests.session()
        self.version = '0.11'
        self.rid = 0

    def print(self, text):
        """internal print only if debug is true, used internally"""
        if self.debug:
            print(text)

    def get_id(self):
        """internal get id, increase everytime"""
        self.rid = self.rid+1
        return self.rid
 
    def get_json(self, json_request):
        """ internal get json """
        req = self.session.post(self.url, data=json_request)
        return(req.json())

    def get_series(self):
        """ get series """
        json_request = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "filter": {"field": "playcount", "operator": "is", "value": "0"}, "properties": ["art", "genre", "plot", "title", "originaltitle", "year", "rating", "thumbnail", "playcount", "file", "fanart"], "sort": { "order": "ascending", "method": "label" } }, "id": "libTvShows"}' 
        output = self.get_json(json_request)['result']['tvshows']
        return(output)

    def set_episodedetails(self, episodeid, playcount=0, position=0):
        if playcount > 0:
            rid = self.get_id()
            json_request = """ {
                                    "id": %d,
                                    "jsonrpc": "2.0",
                                    "method": "VideoLibrary.SetEpisodeDetails",
                                    "params": {
                                        "episodeid": %d,
                                        "playcount": %d
                                    }
                               }""" % (rid, episodeid, playcount)
            output = self.get_json(json_request)
            return output['result'] == 'OK'
        if position > 0:
            rid = self.get_id()
            json_request = """ {
                                    "id": %d,
                                    "jsonrpc": "2.0",
                                    "method": "VideoLibrary.SetEpisodeDetails",
                                    "params": {
                                        "episodeid": %d,
                                        "resume": {
                                            "position": %d,
                                            "total": 0
                                        }
                                    }
                               }""" % (rid, episodeid, position)
            output = self.get_json(json_request)
            return output['result'] == 'OK'


    def get_episodes(self, tvshow, sort=False):
        """ get episoded """
        rid = self.get_id()
        json_request = """ {
                                "id": %d,
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
        output = self.get_json(json_request % (rid, tvshow))['result']['episodes']
        if sort:
            output.sort(key=operator.itemgetter('episode'))
            output.sort(key=operator.itemgetter('season'))
        return(output)

