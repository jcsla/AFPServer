# encoding: utf-8

################################################################################
# MACROBOX Main
#-------------------------------------------------------------------------------
# author: Taehong Kim / MUTEKLAB Co., Ltd.
# email: peppy0510@hotmail.com / thkim@muteklab.com
################################################################################

import sys, hashlib
sys.path.insert(0, "echoprint-server/API")
from fp import *

_fp_solr = solr.SolrConnectionPool("http://localhost:8502/solr/fp")
_hexpoch = int(time.time() * 1000)
logger = logging.getLogger(__name__)
_tyrant_address = ['localhost', 1978]
_tyrant = None


def ingest(fingerprint_list, do_commit=True, local=False, split=True):
	if not isinstance(fingerprint_list, list):
		fingerprint_list = [fingerprint_list]
		
	docs = []
	codes = []
	for fprint in fingerprint_list:
		if not ("track_id" in fprint and "fp" in fprint and "codever" in fprint):
			raise Exception("Missing required fingerprint parameters (track_id, fp, codever")
		if "import_date" not in fprint:
			fprint["import_date"] = IMPORTDATE
		if split:
			print 'sdfjklsdfjsdklfjklsdkfjsdlk'
			split_prints = split_codes(fprint)

	if split:
		docs.extend(split_prints)
		codes.extend(((c["track_id"].encode("utf-8"), c["fp"].encode("utf-8")) for c in split_prints))
	else:
		docs.extend(fingerprint_list)
		codes.extend(((c["track_id"].encode("utf-8"), c["fp"].encode("utf-8")) for c in fingerprint_list))

	print docs
	print codes

	if local:
		return local_ingest(docs, codes)

	with solr.pooled_connection(_fp_solr) as host:
		host.add_many(docs)

	get_tyrant().multi_set(codes)

	if do_commit:
		commit()


def delete(track_ids, do_commit=True, local=False):
	# delete one or more track_ids from the fp flat. 
	if not isinstance(track_ids, list):
		track_ids = [track_ids]

	# delete a code from FP flat
	if local:
		return local_delete(track_ids)

	with solr.pooled_connection(_fp_solr) as host:
		for t in track_ids:
			host.delete_query("track_id:%s*" % t)

	track_ids = [t.encode('utf-8') for t in track_ids]    
	try:
		get_tyrant().multi_del(track_ids)
	except KeyError:
		pass
	
	if do_commit:
		commit()
