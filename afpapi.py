# encoding: utf-8

################################################################################
# AFPAPI
#-------------------------------------------------------------------------------
# author: Taehong Kim / MUTEKLAB Co., Ltd.
# email: peppy0510@hotmail.com / thkim@muteklab.com
################################################################################

################################################################################
# Project Environment
#-------------------------------------------------------------------------------
PASSWORD = u'1q2w3e4r'
HOST, PORT = ('0.0.0.0', 80)
#-------------------------------------------------------------------------------
import fp_mod as fp
from operator import itemgetter
import os, sys, re, web, json, subprocess
#-------------------------------------------------------------------------------
# end of Project Environment
################################################################################

################################################################################
# Utilities
#-------------------------------------------------------------------------------
def remap_key(data):
	# remap json format for server and client
	keymap = (
		('key', 'track_id'),
		('keys', 'track_ids'),
		)
	#---------------------------------------------------------------------------
	for left_key, right_key in [(x, y) for x, y in keymap if x != y]:
		if data.has_key(left_key):
			data[right_key] = data.pop(left_key)
		elif data.has_key(right_key):
			data[left_key] = data.pop(right_key)
	return data
#-------------------------------------------------------------------------------
def is_admin_password(password):
	if password == PASSWORD:
		return True
	return False
#-------------------------------------------------------------------------------
# end of Utilities
################################################################################

################################################################################
# URLS
#-------------------------------------------------------------------------------
urls = (
	'/query', 'Query',
	'/query?(.*)', 'Query',
	'/admin/ingest', 'AdminIngest',
	'/admin/delete', 'AdminDelete',
	'/admin/status', 'AdminStatus',
)
#-------------------------------------------------------------------------------
# end of URLS
################################################################################

################################################################################
# Query
#-------------------------------------------------------------------------------
# indata: fp
#         codever
# return: method
#         status
#         key(track_id)
#         actual_score
#         solr_score
#         program_name
#         program_entry
#-------------------------------------------------------------------------------
class Query:
	#---------------------------------------------------------------------------
	def POST(self):
		data = web.data()
		data = remap_key(json.loads(data))
		resp = fp.best_match_for_query(data['fp'])
		track_id, program_name, program_entry = (resp.TRID, None, None)
		if track_id is not None:
			# meta = fp.metadata_for_track_id(track_id)
			# print dir(meta)
			# print dir(resp)
			# print dir(resp.metadata)
			program_name = resp.metadata['program_name']
			program_entry = resp.metadata['program_entry']
		if resp.metadata.has_key('score') == False:
			resp.metadata['score'] = 0.0
		result = {'method': 'query', 'status': 'ok', 'track_id': track_id,\
			'actual_score': resp.score, 'solr_score': resp.metadata['score'],
			'program_name': program_name, 'program_entry': program_entry}
		return json.dumps(remap_key(result))
	#---------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# end of Query
################################################################################

################################################################################
# AdminIngest
#-------------------------------------------------------------------------------
# indata: password
#         key(track_id)
#         fp
#         codever
# return: method
#         status
#         key(track_id)
#-------------------------------------------------------------------------------
class AdminIngest:
	#---------------------------------------------------------------------------
	def POST(self):
		data = web.data()
		data = remap_key(json.loads(data))
		if data.has_key('password') == False:
			return web.webapi.BadRequest()
		if is_admin_password(data['password']) == False:
			return web.webapi.BadRequest()
		data.pop('password')
		#-----------------------------------------------------------------------
		if data['track_id'] is '':
			return web.webapi.BadRequest()
		if data['codever'] is '':
			return web.webapi.BadRequest()
		# data['fp'] = data['fp'].decode('utf-8')
		# if re.match('[A-Za-z\/SolrException\+\_\-]', data['fp']) is not None:
		# 	return web.webapi.BadRequest()
		code_string = fp.decode_code_string(data['fp'])
		if code_string is None:
			return web.webapi.BadRequest()
		data[u'fp'] = code_string
		#-----------------------------------------------------------------------
		fp.ingest(data, do_commit=True, local=False, split=False)
		result = {'method': 'ingest', 'status':'ok',\
			'track_id':data[u'track_id']}
		return json.dumps(remap_key(result))
	#---------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# end of AdminIngest
################################################################################

################################################################################
# AdminDelete
#-------------------------------------------------------------------------------
# indata: password
#         key(track_id)
# return: method
#         status
#         key(track_id)
#-------------------------------------------------------------------------------
class AdminDelete:
	#---------------------------------------------------------------------------
	def POST(self):
		data = web.data()
		data = remap_key(json.loads(data))
		if data.has_key('password') == False:
			return web.webapi.BadRequest()
		if is_admin_password(data['password']) == False:
			return web.webapi.BadRequest()
		data.pop('password')
		#-----------------------------------------------------------------------
		if data['track_id'] is '':
			return web.webapi.BadRequest()
		#-----------------------------------------------------------------------
		track_id = data['track_id']
		fp.delete(track_id, do_commit=True, local=False)
		result = {'method': 'delete', 'status':'ok', 'track_id': track_id}
		return json.dumps(remap_key(result))
	#---------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# end of AdminDelete
################################################################################

################################################################################
# AdminStatus
#-------------------------------------------------------------------------------
# indata: password
# return: method
#         status
#         key(track_id)
#-------------------------------------------------------------------------------
class AdminStatus:
	#---------------------------------------------------------------------------
	def POST(self):
		data = web.data()
		data = remap_key(json.loads(data))
		if data.has_key('password') == False:
			return web.webapi.BadRequest()
		if is_admin_password(data['password']) == False:
			return web.webapi.BadRequest()
		data.pop('password')
		#-----------------------------------------------------------------------
		command = 'tcrmgr inform -port 1978 localhost'
		p = subprocess.Popen(command, shell=True,\
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(result, errs) = p.communicate()
		record_number = result.split(os.linesep)[0].split(' ')[-1]
		#-----------------------------------------------------------------------
		command = 'tcrmgr list -port 1978 localhost'
		p = subprocess.Popen(command, shell=True,\
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(result, errs) = p.communicate()
		track_ids = [track_id for track_id\
			in result.split(os.linesep) if track_id != '']
		#-----------------------------------------------------------------------
		result = {'method': 'status', 'status':'ok',\
			'record_number': record_number, 'track_ids': track_ids}
		return json.dumps(remap_key(result))
	#---------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# end of AdminStatus
################################################################################

################################################################################
# Main Entry
#-------------------------------------------------------------------------------
class WebApplication(web.application): 
	def run(self, host='0.0.0.0', port=8080, *middleware): 
		func = self.wsgifunc(*middleware) 
		return web.httpserver.runsimple(func, (host, port)) 
#-------------------------------------------------------------------------------
application = WebApplication(urls, globals())#.wsgifunc()
#-------------------------------------------------------------------------------
if __name__ == "__main__":
	application.run(host=HOST, port=PORT)
#-------------------------------------------------------------------------------
# end of Main Entry
################################################################################
	
