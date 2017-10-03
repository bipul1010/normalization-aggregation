import json
import pysolr






def solrDataStorageSplittingList (docs,size_per_bundle,solr_address,filename):

	solr = pysolr.Solr (solr_address,timeout = 10)
	docs_split = [docs[i:i+size_per_bundle] for i in xrange (0,len (docs),size_per_bundle)]
	for idx,doc in enumerate (docs_split):
		print idx," " ,filename
		solr.add (doc,"json")


def print_hello():
	print "hello"

if __name__ == "__main__":

	file_list = ["company_kb.json","edu_org.json","location_kb.json","major.json","degree.json"]
	for filename in file_list:
		docs = json.load (open (filename))
		docs = docs if docs [0].get ("normalized_name") else docs [1:]
		print len (docs)
		solrDataStorageSplittingList (docs,20000,"http://localhost:8983/solr/knowledge_base",filename)
