import pysolr
import json
import fuzzy
import math


def tfidf (freq,no_documents):

	return (1 + math.log (freq)) * (math.log (float (no_documents) / float (freq)))


def variations (word,abbreviation):
	word = word.strip ()
	variants = []
	variants.append (word)
	if len (word.split ()) > 1:
		variants.append ("".join (word.split ()).lower ())
		if abbreviation:
			if word.lower ().find ("and") != -1:
				abb = "".join ([each_word[0].lower () if each_word.lower () != "and" else "&" for each_word in word.split ()])
				variants.append (abb)
				abb = "".join ([each_word[0].lower () for each_word in word.split () if each_word.lower () != "and"])
				variants.append (abb)
			else:
				abb = "".join ([each_word[0].lower () for each_word in word.split () if each_word.lower () != "and"])
				variants.append (abb)

	return variants

def skillsPopulate (docs):

	global_search = dict ()
	for idx,doc in enumerate (docs):
		print idx
		skills_list = doc.get ("skills")
		for skill in skills_list:
			if skill.find ("See") != -1 and skill.find ("+") != -1:
				continue
			else:
				if skill.lower ().strip () != ".net":
					skill = skill.strip (".")
				if skill.lower () in global_search:
					if skill in global_search [skill.lower ()]:
						global_search [skill.lower ()][skill] += 1
					else:
						global_search [skill.lower ()][skill] = 1
				else:
					global_search [skill.lower ()] = dict ()
					global_search [skill.lower ()][skill] = 1

	return global_search


def expPopulate (docs,key):
	global_search = dict ()
	for idx,doc in enumerate (docs):
		print idx
		exp_list = doc.get ("educations")
		for experience in exp_list:
			exp_doc = json.loads (experience)
			if exp_doc.get (key):
				title = exp_doc [key].strip (".").strip ()
				if title.lower () in global_search:
					if title in global_search [title.lower ()]:
						global_search [title.lower ()][title] += 1
					else:
						global_search [title.lower ()][title] = 1

				else:
					global_search [title.lower ()] = dict ()
					global_search [title.lower ()][title] = 1

	return global_search
	


def normalizationWords (global_dic,attribute,no_documents,freq_threshold):

	global_list = []
	total_freq = sum ([sum (global_dic [word].values ()) for word in global_dic])
	for word in global_dic:
		local_dic = {}
		local_dic ["attribute"] = attribute
		word_max_freq = [each_word for each_word in global_dic [word] if global_dic [word][each_word] == max (global_dic [word].values ())][0]
		local_dic ["normalized_name"]  = word_max_freq
		local_dic ["phonetic_name"] = fuzzy.nysiis (word_max_freq)
		local_dic ["id"] = "".join ((attribute + "#!#" + word).split ())
		local_dic ["frequency"] = sum (global_dic [word].values ())
		local_dic ["tfidf"] = tfidf (sum (global_dic [word].values ()),no_documents)
		local_dic ["probability_attribute"] = float (sum (global_dic [word].values ())) / float (total_freq)
		local_dic ["variants"] =  variations (word_max_freq,True)
		if local_dic.get ("frequency") and local_dic ["frequency"] > freq_threshold:
			global_list.append (local_dic)


	return global_list











if __name__ == "__main__":

	#fw = open ("skills_kb.json","w")
	fw = open ("major.json","w")
	solr = pysolr.Solr ("http://localhost:8983/solr/resume_data",timeout = 10)
	#docs = solr.search (q = "skills:*",fl = "skills",**{"start":0,"rows":1000000}).docs
	#docs = solr.search (q = "experiences:*",fl = "experiences",**{"start":0,"rows":10000000}).docs
	docs = solr.search (q = "educations:*",fl = "educations",**{"start":0,"rows":10000000}).docs
	#global_search = skillsPopulate (docs)
	global_search = expPopulate (docs,"major")
	print "Normalization of words.."
	global_list = normalizationWords (global_search,"major",len (docs),60)
	fw.write (json.dumps (global_list))


