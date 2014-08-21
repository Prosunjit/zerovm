from lexical_analyzer import LexicalAnalyzer
from PythonJsonObj import PyObjTree, PyJSOb
import constant as constant
import utility as utl
import sys
import policy as Policy
from access_control import NodeHierarchy

class ObQuery:
	def __init__(self, root_ob):
		self.tree_root = root_ob
		 

	def _gapvalue(self,gap_key, obj):
		r = []

		'''only object type has primitve member of {k:v} format. In Array object, primitive members are only string, or number. 
		so, need not to check prim_mem of array object '''

		if obj.type == "OBJECT":
			for o in obj.prim_mem:
				(k,v) =  o.items()[0]
				if k == gap_key:
					r.append(v)
		for o in obj.obj_mem:
			for (k,v) in o.items():
				if k == gap_key:
					r.append(v)
				else:
					r = r + self._gapvalue(gap_key,v)

		for o in obj.array_mem:
			if isinstance(o,PyJSOb):
				r = r + self._gapvalue(gap_key,o)
		return r
		pass	 
	def query(self,path):
		
		if path == "/":
			#print "returing root obj----------------"
			#print id( self.tree_root)
			return [self.tree_root]
		path_token = LexicalAnalyzer(path).token_pair()
		ini_nodes = [self.tree_root]
		final_nodes=[]		
		token_pair = path_token

		for tp in token_pair:

			(t1,t2) = tp
			final_nodes = []
			 
			if t1 == "child":
				for root in ini_nodes:
					# looking into the object
					for n in root.obj_mem:
						for (k,v) in n.items():
							if k == t2:
								final_nodes.append(v)
					for n in root.prim_mem:
						(k,v) = n.items()[0]
						if k == t2:
							final_nodes.append(v)
				pass
				 
			elif t1 == "index":
				for root in ini_nodes:
					t2 = int(t2)
					try:
						n = root.array_mem[t2]
					except:
						pass
				final_nodes.append(n)
				pass
				 
			elif t1 == "gap":
				for root in ini_nodes:
					final_nodes = final_nodes + self._gapvalue(t2,root)
				pass
			ini_nodes = final_nodes
		return final_nodes

	
	def _authorized_only(self, job, label_hierarchy, user_clearance):
		# check descendant nodes for clearance
		#array_mem = []
		#obj_mem = []
		#prim_mem = []
		r_obj = []
		#print job
		if job.type == "OBJECT":
			# check for obj_members
			for ob in job.obj_mem:
				(key,value) = ob.items()[0]
				value = self._authorized_only(value,label_hierarchy, user_clearance)
				if value:
					r_obj = r_obj + [{key:value}] # if obj, pass key,value dictionary
			pass
		elif job.type == "ARRAY":
			
			for ar in job.array_mem:
				value = self._authorized_only(ar, label_hierarchy, user_clearance)
				if value:
					r_obj = r_obj + [value]
			pass
		else:
			pass

		# check if job is has clearance, a function shold be called here
		if  job.label != constant.DEFAULT_LABEL and label_hierarchy.check(user_clearance,job.label) : 
			#remove all existing array, ob members
			job.array_mem = []
			job.obj_mem = []

			# return None when a json obj has no member

			if len(r_obj) == 0 and len (job.prim_mem) == 0:
				return None

			for o in r_obj:
				if type(o) is dict:
					(k,v) = o.items()[0]
					job.add_obj_mem(key=k, value=v)
				else:
					job.add_array_mem(o)
			pass
			return job
		else:
			ob = PyJSOb()
			if len(r_obj) == 0:
				return None
			for mem in r_obj:
				if type(mem) == dict:
					(k,v) = mem.items()[0]
					ob.add_obj_mem(key=k, value = v)
				elif isinstance(mem,PyJSOb)  and mem.type == constant.ARRAY:
					ob.add_array_mem(mem)
			
			return ob
		

		
		


	# this method do query without ac, then apply access control on the result
	# not considering clearance lattice.

	def ac_query(self, path, label_hierarchy, user_clearance):
		q_res = self.query(path)
		authorized_list = []
		for ob in q_res:
			authorized_list.append( self._authorized_only(ob,label_hierarchy, user_clearance))
			pass

		return authorized_list
		pass

#def test(json_file,policy_file,q_path,user_label=None):
def test(json_file=None, policy_file=None, q_path="/", user_label=None):	
	#run with this command :  python ObQuery.py employee.json /personalRecord

	#build the Json Obj tree here

	if not json_file:
		json_file="jsonac/employee.json"
	if not policy_file:
		policy_file="jsonac/path_label_policy.json"
	


	obj_tree = PyObjTree(utl.LoadJSON(path=json_file).get_json()).get_root()
	#apply labels to obj tree
	obj_tree = Policy.NodeLabeling(obj_tree,label_file=policy_file).appy_labels()
	#print utl.pretty_print (obj_tree.print_json())
	#return 
	#querying against give path

	#print id(obj_tree)
	path = q_path

	nh = NodeHierarchy()
	nh.insert("private","public")
	nh.insert("protected","private")


	oq = ObQuery(obj_tree)

	#print oq.query_on_condition( {'path':'name', 'op':'=', 'value':'Alice'}, obj_tree)
	#return 
	#qry = ["/","/personalRecord","/","/personalRecord/identification"]
	qry = [path]


	for q in qry: 
		#print "path is {}".format(q)
	
		#if len(sys.argv) >=4 :
		if user_label:
			res = oq.ac_query(q,nh,user_label)
		else:
			res = oq.query(q)
		# we need to iterate through the res. there can be more than one result.
		#print (res)
		for r in res:
			#print r
			if type(r) is dict:
				(k,v) = r.items()[0]
				print utl.pretty_print ( v.print_json() )
				pass
			elif isinstance(r,PyJSOb):
				#print r.print_json()
				print utl.pretty_print ( r.print_json() )
			else:
				print r
	
	#print utl.pretty_print ( obj_tree.print_json() )
	


def test2():
	print "hello world"

if __name__ == "__main__":
	print "hello world"
	test("employee.json","path_label_policy.json","/personalRecord/identification","protected")
