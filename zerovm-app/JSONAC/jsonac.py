#!/usr/bin/python
import sys
import  jsonac

print "hello world from jsonac.py"
if __name__ == "__main__":
	if len(sys.argv) >= 3:
		path=sys.argv[1]
		u_label= sys.argv[2]
	elif len(sys.argv) >=2 :
		path=sys.argv[1]
	else:
		path="/"
		u_label="protected"
	jsonac.ObQuery.test(q_path=path, user_label=u_label)
