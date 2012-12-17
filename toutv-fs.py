#!/usr/bin/env python

import os, stat, errno
import threading, time
import fuse

import toutv.client;
import toutv.cache;
import time

fuse.fuse_python_api = (0, 2)

hello_str = open('/home/simark/Downloads/out.mp4', 'rb').read()

class MyStat(fuse.Stat):
	def __init__(self):
		self.st_mode = 0
		self.st_ino = 2
		self.st_dev = 2
		self.st_nlink = 2
		self.st_uid = 1000
		self.st_gid = 1000
		self.st_size = 0
		self.st_atime = 0
		self.st_mtime = time.time()
		self.st_ctime = 0

class TouTVFS(fuse.Fuse):
	def __init__(self, *args, **kwargs):
		super(TouTVFS, self).__init__(*args, **kwargs)
		
		transport = toutv.client.TransportJson()
		cache = toutv.cache.CacheShelve('.toutv_cache')
		self.client = toutv.client.ToutvClient(transport = transport, cache = cache)
		
	def get_parts(self, path):
		return [x for x in path.split('/') if len(x) > 0]
	
	def getattr(self, path):
		print "+ getattr " + path
		st = MyStat()

		parts = self.get_parts(path)
	
		# /
		if len(parts) == 0:
			st.st_mode = stat.S_IFDIR | 0777
			st.st_nlink = 2
		# Une emission
		elif len(parts) == 1:
			print "C'est une emission"
			emissions = self.get_emissions_by_name()
			if parts[0] in emissions:
				st.st_mode = stat.S_IFDIR | 0777
				st.st_nlink = 1
				st.st_size = 0
			else:
				st = -errno.ENOENT
		# Un episode
		elif len(parts) == 2:
			emission_name = parts[0]
			episode_name = parts[1]
			episode_name = episode_name.split('-')[0]

			emissions = self.get_emissions_by_name()
			if emission_name in emissions:
				emission = emissions[emission_name]
				episodes = self.get_episodes_by_name(emission.Id)
				if episode_name in episodes:
					st.st_mode = stat.S_IFREG | 0777
					st.st_size = len(hello_str)
				else:
					print "Episode no exists"
					print "Je cherchais " + episode_name
					print "Les cles etaient " + str(episodes.keys())
					st = -errno.ENOENT
			else:
				st = -errno.ENOENT
		else:
			print "No exists"
			st = -errno.ENOENT
		return st

	def readdir(self, path, offset):
		print "+ readdir " + path
		yield fuse.Direntry('.')
		yield fuse.Direntry('..')
		
		parts = self.get_parts(path)
	
		# Liste des emissions
		if len(parts) == 0:
			emissions = self.get_emissions_by_name()
			for name in emissions:
				yield fuse.Direntry(name)
		# Liste des episodes
		elif len(parts) == 1:
			emissions = self.get_emissions_by_name()
			if parts[0] in emissions:
				emission = emissions[parts[0]]
				episodes = self.client.get_episodes_for_emission(emission.Id)
				for i in episodes:
					episode = episodes[i]
					generated_name = str(episode.SeasonAndEpisode.encode('utf-8') + "-(titre todo).mp4")
					yield fuse.Direntry(generated_name)
			else:
				print "Emission pas trouvee " + parts[0]

	def open(self, path, flags):
		print "+ open " + path
		if not path.endswith('.mp4'):
			print "IT NO EXISTS open"
			return -errno.ENOENT
		accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
		if (flags & accmode) != os.O_RDONLY:
			return -errno.EACCES

	def read(self, path, size, offset):
		
		print "+ read " + path
		
		if not path.endswith('.mp4'):
			print "IT NO EXISTS read"
			return -errno.ENOENT
		slen = len(hello_str)
		if offset < slen:
			if offset + size > slen:
				size = slen - offset
			buf = hello_str[offset:offset+size]
		else:
			buf = ''
		return buf

	def get_emissions_by_name(self):
		pr = self.client.get_page_repertoire()
		er = pr["emissionrepertoire"]
		ret = {}
		for i in er:
			emission = er[i]
			if emission.NombreEpisodes > 0:
				try:
					name = str(emission.Titre.encode('utf-8'))
					ret[name] = emission
				except UnicodeEncodeError as e:
					print e
					pass

		return ret
	
	def get_episodes_by_name(self, emission_id):
		eps = self.client.get_episodes_for_emission(emission_id)
		ret = {}

		for ep in eps:
			ret[eps[ep].SeasonAndEpisode] = ep

		return ret

def main():
	usage="""
Tou.TV fs

""" + fuse.Fuse.fusage
	server = TouTVFS(version="%prog " + fuse.__version__,
					 usage=usage,
					 dash_s_do='setsingle')

	server.parse(errex=1)
	server.main()

if __name__ == '__main__':
	main()
