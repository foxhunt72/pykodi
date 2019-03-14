#
import requests
import json
import operator


from pprint import pprint




class foxhunt_pykodi:
    """Dit is een class

    usage: ....

    """

    def __init__(self, kodi_url, debug=False, username=None, password=None,rpcpath='jsonrpc'):
        self.url = kodi_url
        self.debug = debug
        self.session = requests.session()
        self.version = '0.2'
        self.rid = 0
        self.series = None
        self.username = username
        self.password = password
        self.rpcpath = rpcpath

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
        self.print('get json')
        req = self.session.post(self.url+'/'+self.rpcpath, data=json_request, auth=(self.username,self.password))
        if req.status_code != 200:
            # TODO more error handing
            self.print('result: %d' % (req.status_code))
            pprint(req)
        try:
            json = req.json()
        except ValueError:
            json = None
        return(json)

    def get_shows(self,cache=True):
        """ get series """
        if (cache == True) and (self.series != None):
            return(self.series)
        json_request = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": { "filter": {"field": "playcount", "operator": "is", "value": "0"}, "properties": ["art", "genre", "plot", "title", "originaltitle", "year", "rating", "thumbnail", "playcount", "file", "fanart"], "sort": { "order": "ascending", "method": "label" } }, "id": "libTvShows"}' 
        output = self.get_json(json_request)
        if output == None:
            return(None)
        try:
           self.series = output['result']['tvshows']
        except KeyError:
           self.series = None
        return(self.series)

    def get_show(self,search_show):
        """ get show """
        series=self.get_shows()
        for show in series:
            #self.print('title: %s ? %s' % (show['title'],search_show))
            if show['title'] == search_show:
                self.print('>>>>>>>>   ')
                return(show)
        return(None)

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


    def _prepare_download(self, path):
        """ get preparedownload url """
        rid = self.get_id()
        json_request = """ {
                                "id": %d,
                                "jsonrpc": "2.0",
                                "method": "Files.PrepareDownload",
                                "params": {
                                	"path": "%s"
                                    }
                           } """ % (rid, path)
        output = self.get_json(json_request)
        url_path=output['result']['details']['path']
        return url_path

    def _download_file(self,path,path_out):
        """ download file """
        url_path=self._prepare_download(path)
        if url_path == None:
            self.print('_download_file: failed prepare download: %s' % (path))
            return(False)
        self.print('get download')
        req = self.session.post(self.url+'/'+url_path, auth=(self.username,self.password), stream=True)
        if req.status_code != 200:
            # TODO more error handing
            self.print('result: %d' % (req.status_code))
            pprint(req)
        with open(path_out,'wb') as f:
            for chunk in req.iter_content():
                f.write(chunk)


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

