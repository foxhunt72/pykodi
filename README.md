# pykodi
python library for api connection to tvshows library


v0.1

example:


from foxhunt_pykodi import foxhunt_pykodi

kodi=foxhunt_pykodi('http://127.0.0.1:8080/jsonrpc',debug=True)


series=kodi.get_series()

for show in series:
    print(show['title']+'   '+str(show['tvshowid']))


episodes=kodi.get_episodes(6,sort=True)
for episode in episodes:
    print("%3d %3d :%2d   (%d / %d)" % (episode['season'],episode['episode'],episode['playcount'],episode['resume']['position'],episode['resume']['total']))

