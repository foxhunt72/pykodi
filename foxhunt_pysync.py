#!/usr/bin/python


from foxhunt_pykodi import foxhunt_pykodi
from pprint import pprint
import operator
import os


def foxhunt_pysync(kodi_master_url, kodi_slave_url, slave_dir, sync_shows, kodi_master_auth=None, kodi_slave_auth=None, debug=False,delete_played_on_slave=True):
    global total_episodes
    global synced_file
    global sync_slave_library
    synced_file = 0
    default_episodes = 2
    sync_slave_library = False
    kodi = foxhunt_pykodi(kodi_master_url, auth=kodi_master_auth, debug=debug)
    kodi_slave = foxhunt_pykodi(
        kodi_slave_url, auth=kodi_slave_auth, debug=debug)

    # wait until connection to master
    kodi.wait_for_connection(sleep_time=20)
    # wait until connection to slave
    kodi_slave.wait_for_connection(sleep_time=20)

    destDir = slave_dir
    check_shows = sync_shows

    def sync_playcount_position():
        kodi.episodes_tvshow = None
        kodi_slave.episodes_tvshow = None
        series = kodi_slave.get_shows()
        if series != None:
            for slave_serie in series:
                print(slave_serie['title'])
                for slave_episode in kodi_slave.get_episodes(slave_serie['tvshowid'], sort=True):
                    print("season: %3d    episode: %3d :%2d    played on slave: (%d / %d)" %
                          (slave_episode['season'], slave_episode['episode'], slave_episode['playcount'], slave_episode['resume']['position'], slave_episode['resume']['total']))
                    master_episode = kodi.get_episode(
                        slave_serie['title'], slave_episode['season'], slave_episode['episode'])
                    if master_episode != None:
                        if master_episode['playcount'] > slave_episode['playcount']:
                            kodi_slave.set_episodedetails(
                                slave_episode['episodeid'], playcount=master_episode['playcount'])
                            print('setting slave playcount')
                            continue
                        if master_episode['playcount'] < slave_episode['playcount']:
                            kodi.set_episodedetails(
                                master_episode['episodeid'], playcount=slave_episode['playcount'])
                            print('setting master playcount')
                            print('setting master playcount to %d' % (slave_episode['resume']['position']))
                            continue
                        if master_episode['resume']['position'] > slave_episode['resume']['position']:
                            kodi_slave.set_episodedetails(
                                slave_episode['episodeid'], position=master_episode['resume']['position'])
                            print('setting slave position to %d' % (master_episode['resume']['position']))
                            continue
                        if master_episode['resume']['position'] < slave_episode['resume']['position']:
                            kodi.set_episodedetails(
                                    master_episode['episodeid'], position=slave_episode['resume']['position'])
                            print('setting master position to %d' % (slave_episode['resume']['position']))
                            continue
                        if master_episode['playcount'] > 0 and slave_episode['playcount'] > 0:
                            if os.path.exists(slave_episode['file']):
                                if delete_played_on_slave:
                                  print('delete file: '+slave_episode['file'])
                                  os.remove(slave_episode['file'])
                                else:
                                  print('not deleted file: '+slave_episode['file'])
                            sync_slave_library = True

    def check_and_download():
        total_episodes = 0
        synced_file = 0
        for showname in check_shows:
            show = kodi.get_show(showname['name'])
            show_basename = os.path.basename(show['file'].rstrip('/'))
            if debug:
                print('basename: %s    %s' % (show_basename, show['file']))
            if 'episodes' in showname:
                sync_episodes = showname['episodes']
            else:
                sync_episodes = default_episodes
            if show == None:
                print("Show not found...")
                exit(0)
            print('Show: %s  (sync: %d)' % (show['title'], sync_episodes))
            episodes = kodi.get_episodes(show['tvshowid'], sort=True)
            done_episodes = 0
            for episode in episodes:
                if episode['playcount'] == 0:
                    print("%30s season: %3d episode: %3d" %
                          (show['title'], episode['season'], episode['episode']))
                    if episode['file'].startswith(show['file']):
                        substr = episode['file'][len(show['file']):]
                        if debug:
                            print(">>> "+substr)
                        full_out_path = destDir+'/'+show_basename+'/'+substr
                        if debug:
                            print("full path: %s" % (full_out_path))
                        if not os.path.isfile(full_out_path):
                            if debug:
                                print('create path')
                            os.makedirs(os.path.dirname(
                                full_out_path), exist_ok=True)
                            synced_file = synced_file + 1
                            print('downloading.....')
                            kodi._download_file(episode['file'], full_out_path)
                    done_episodes += 1
                    total_episodes += 1
                    if done_episodes >= sync_episodes:
                        break

    sync_playcount_position()
    check_and_download()
    if synced_file > 0 or sync_slave_library:
        kodi_slave.scan_videolibrary()
        print('sleeping 30s for libary scanning')
        time.sleep(30)
    sync_playcount_position()
