# encoding: utf-8

################################################################################
# AFPTOOL
#-------------------------------------------------------------------------------
# author: Taehong Kim / MUTEKLAB Co., Ltd.
# email: peppy0510@hotmail.com / thkim@muteklab.com
################################################################################

# ffmpeg -i input.avi -ac 1 -ar 11025 output.wav

################################################################################
# Project Environment
#-------------------------------------------------------------------------------
PASSWORD = u'1q2w3e4r'
HOST, PORT = ('211.110.33.122', 80)
LOCALHOST_REDIRECTION = ('172.27.245.169')
#-------------------------------------------------------------------------------
import os, sys, json, socket, httplib, subprocess, datetime
#-------------------------------------------------------------------------------
if sys.platform.startswith('win'):
	CODEGEN_BINARY = u'codegen.exe'
	CODEGEN_BINARY = os.path.abspath(CODEGEN_BINARY)
	if os.path.isfile(CODEGEN_BINARY) == False:
		CODEGEN_BINARY = u'echoprint-codegen\windows\Release\codegen.exe'
		CODEGEN_BINARY = os.path.abspath(CODEGEN_BINARY)
elif sys.platform.startswith('linux'):
	CODEGEN_BINARY = u'echoprint-codegen'
if socket.gethostbyname(socket.gethostname()) in LOCALHOST_REDIRECTION:
	HOST, PORT = ('localhost', PORT)
#-------------------------------------------------------------------------------
# end of Project Environment
################################################################################

################################################################################
# Utilities
#-------------------------------------------------------------------------------
def codegen(filename, seconds_start=0, seconds_duration=120):
	command = ' '.join(('"'+CODEGEN_BINARY+'"',\
		'"'+filename+'"', str(seconds_start), str(seconds_duration)))
	p = subprocess.Popen(command, shell=True,\
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	# print command
	(result, errs) = p.communicate()
	try: data = json.loads(result)[0]
	except: return None
	# print data
	return data
#-------------------------------------------------------------------------------
def make_req(url='/query', body_data='', host=HOST, port=PORT, timeout=10):
	headers = {"Content-type": "application/x-www-form-urlencoded; charset=utf-8",
		"Accept": "text/plain"}
	headers['Connection'] = 'close'
	resp = None
	try:
		conn = httplib.HTTPConnection(host, port, timeout=timeout)
		conn.request('POST', url, body_data.encode('utf-8'), headers)
		resp = conn.getresponse()
	except:
		pass
	finally:
		conn.close()
	return resp
#-------------------------------------------------------------------------------
# end of Utilities
################################################################################

################################################################################
# Query Ingest Delete
#-------------------------------------------------------------------------------
def query(filename):
	filename = os.path.abspath(filename)
	data = codegen(filename)
	body_data = {
		'fp': data['fp'],
		'codever': data['codever'],
		}
	resp = make_req(url='/query', body_data=json.dumps(body_data))
	try: return json.loads(resp.read())
	except: return None
#-------------------------------------------------------------------------------
def ingest(track_id, filename):
	filename = os.path.abspath(filename)
	data = codegen(filename)
	# now = datetime.datetime.utcnow()
	# import_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
	# import_date, program_name, program_entry, brocast_date, items
	body_data = {
		'password': PASSWORD,
		'key': track_id,
		'fp': data['fp'],
		'codever': data['codever']
		}
	resp = make_req(url='/admin/ingest', body_data=json.dumps(body_data))
	try: return json.loads(resp.read())
	except: return None
#-------------------------------------------------------------------------------
def delete(track_id):
	body_data = {'password': PASSWORD, 'key': track_id}
	resp = make_req(url='/admin/delete', body_data=json.dumps(body_data))
	try: return json.loads(resp.read())
	except: return None
#-------------------------------------------------------------------------------
def status():
	body_data = {'password': PASSWORD}
	resp = make_req(url='/admin/status', body_data=json.dumps(body_data))
	try: return json.loads(resp.read())
	except: return None
#-------------------------------------------------------------------------------
# end of Query Ingest Delete
################################################################################

################################################################################
# Main Entry
#-------------------------------------------------------------------------------
def manual():
	print '\n    < < <  Catch Player AFPTOOL  > > >\n'
	print '    python afpapi.py query [filename]'
	print '    python afpapi.py ingest [track_id] [filename]'
	print '    python afpapi.py delete [track_id]'
	print '    python afpapi.py status\n'
#-------------------------------------------------------------------------------
if __name__ == "__main__":
	if len(sys.argv) == 1:
		manual()
	elif sys.argv[1].lower() == 'query':
		filename = sys.argv[2]
		query(sys.argv[2])
	elif sys.argv[1].lower() == 'ingest':
		track_id = sys.argv[2]
		filename = sys.argv[3]
		ingest(track_id, filename)
	elif sys.argv[1].lower() == 'delete':
		track_id = sys.argv[2]
		delete(track_id)
	elif sys.argv[1].lower() == 'status':
		print status()
#-------------------------------------------------------------------------------
# end of Main Entry
################################################################################
