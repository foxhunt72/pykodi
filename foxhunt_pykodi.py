#
import requests
import json
import operator
import time
import os


from pprint import pprint


class foxhunt_pykodi:
    """Dit is een class

    usage: ....

    """

    def __init__(self, kodi_url, debug=False, auth=None, rpcpath='jsonrpc'):
        self.url = kodi_url
        self.debug = debug
        self.session = requests.session()
        self.version = '0.2'
        self.rid = 0
        self.series = None
        self.episodes = None
        self.episodes_tvshow = None
        self.auth = auth
        self.rpcpath = rpcpath

    def print(self, text):
        """internal print only if debug is true, used internally"""
        if self.debug:
            print(text)

    def pprint(self, object):
        """internal pprint only if debug is true, used internally"""
        if self.debug:
            pprint(object)

    def get_id(self):
        """internal get id, increase everytime"""
        self.rid = self.rid+1
        return self.rid

    def get_json(self, json_request):
        """ internal get json """
        self.print('get json')
        req = self.session.post(self.url+'/'+self.rpcpath,
                                data=json_request, auth=self.auth)

        self.pprint(req)
        if req.status_code != 200:
            # TODO more error handing
            self.print('result: %d' % (req.status_code))
            self.pprint(req)
        try:
            json = req.json()
        except ValueError:
            json = None
        return(json)

    def get_shows(self, cache=True):
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

    def get_show(self, search_show):
        """ get show """
        series = self.get_shows()
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

    def scan_videolibrary(self):
        """ scan video library """
        rid = self.get_id()
        json_request = """ {
                                "id": %d,
                                "jsonrpc": "2.0",
                                "method": "VideoLibrary.Scan"
                           } """
        output = self.get_json(json_request % (rid))
        return output

    def get_current_profile(self):
        """ get current profile """
        rid = self.get_id()
        json_request = """ {
                                "id": %d,
                                "jsonrpc": "2.0",
                                "method": "Profiles.GetCurrentProfile"
                           } """
        output = self.get_json(json_request % (rid))
        return

    def wait_for_connection(self, sleep_time=60):
        """ wait for connection """
        while True:
            try:
                self.get_current_profile()
                break
            except:
                print("Connection to %s failed. sleeping %d" %
                      (self.url, sleep_time))
                time.sleep(sleep_time)
        return

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
        url_path = output['result']['details']['path']
        return url_path

    def get_file_size(self, path):
        """ get preparedownload url """
        rid = self.get_id()
        json_request = """ {
                                "id": %d,
                                "jsonrpc": "2.0",
                                "method": "Files.GetFileDetails",
                                "params": {
                                	"file": "%s",
                                        "properties": [
                                           "size"
                                        ]
                                    }
                           } """ % (rid, path)
        output = self.get_json(json_request)
        size = output['result']['filedetails']['size']
        return size

    def _download_file(self, path, path_out):
        """ download file """
        url_path = self._prepare_download(path)
        total_size= self.get_file_size(path)
        fsize = 0
        if url_path == None:
            self.print('_download_file: failed prepare download: %s' % (path))
            return(False)
        self.print('get download')
        req = self.session.post(self.url+'/'+url_path,
                                auth=self.auth, stream=True)
        if req.status_code != 200:
            # TODO more error handing
            self.print('result: %d' % (req.status_code))
            pprint(req)
        with open(path_out+'.tmp', 'wb') as f:
            for chunk in req.iter_content(chunk_size=2048):
                fsize += len(chunk)
                print("downloaded %d procent %d bytes (%d)" % (((100*fsize)/total_size),fsize,total_size), end='\r')
                f.write(chunk)
            print("")
        os.rename(path_out+'.tmp',path_out)

    def get_episodes(self, tvshow, sort=False, cache=False):
        """ get episoded """
        if cache:
          if self.episodes_tvshow == tvshow:
              if self.episodes != None:
                  return self.episodes
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
        output = self.get_json(json_request % (rid, tvshow))[
            'result']['episodes']
        if sort:
            output.sort(key=operator.itemgetter('episode'))
            output.sort(key=operator.itemgetter('season'))
        if cache:
            self.episodes = output
            self.episodes_tvshow = tvshow
        return(output)

    def get_episode(self, tvshow, season, episode):
        """ get episode """
        show = self.get_show(tvshow)
        if show == None:
            self.print('show: %s not found' % tvshow)
            return None
        episodes = self.get_episodes(show['tvshowid'],cache=True)
        if episodes == None:
            return None
        for my_episode in episodes:
            if (my_episode['season'] == season) and (my_episode['episode'] == episode):
                return my_episode
        return None
