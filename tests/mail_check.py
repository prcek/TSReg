
import re

#from django
email_re1 = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

#current
email_re2 = re.compile( "^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$" )
jana.piglova@videon-​znojmo.cz

test = ['aa@s-ss.cz', 'jana.piglova@videon-znojmo.cz-']

for e in test:

	if not email_re1.match(e):
		r1 = True
	else:
		r1 = False
	if not email_re2.match(e):
		r2 = True
	else:
		r2 = False
	
	print "%s - %s %s"%(e,r1,r2)
