# -*- coding: utf-8 -*-

from operator import attrgetter
import logging


class FakeStudent():
    x_pair_empty_slot = True
    x_pair_no = 0
    x_pair_complete = False
    x_pair_first = False
    x_pair_second = True
    name = None
    surname = None
    def get_sex(self):
        return None 
 
    def key(self):
        return {'id':''} 

def sort_students_spare_single(students):
    return sorted(students, key=attrgetter('surname','name')) 

def sort_students_spare_school(students):
    return sorted(students, key=attrgetter('school','school_class','addressing','surname','name')) 

def sort_students_spare_pair(students):
    return sorted(students, key=attrgetter('surname','name')) 

def sort_students_single(students):
    return sorted(students, key=attrgetter('surname','name')) 

def sort_students_school(students):
    return sorted(students, key=attrgetter('school','school_class','addressing','surname','name')) 

def sort_students_pair(students):

    d = dict() 
#    dr = dict()
    for s in students:
        d[s.ref_key]=s
        d.setdefault(s.partner_ref_code,None)
#        dr[s.partner_ref_code]=s
       
    dd = dict() 
    pl = []
    for s in students:
        if s.ref_key in dd:
            continue
        p = d[s.partner_ref_code]
        if (not p is None) and p.partner_ref_code == s.ref_key:
            dd[p.ref_key]=p
            dd[s.ref_key]=s
            p.x_pair_complete = True
            s.x_pair_complete = True
            if p.get_sex()=='m':
                p.x_pair_first = True
                s.x_pair_second = True
                pl.append((p,s)) 
            else:
                s.x_pair_first = True
                p.x_pair_second = True
                pl.append((s,p)) 
        else:
            s.x_pair_first = True
            pl.append((s,FakeStudent()))
            
    l = []         
    pno = 0
    for (a,b) in pl:
        pno+=1
        a.x_pair_no = pno
        b.x_pair_no = pno
#        logging.info("============================")            
#        logging.info(a)
#        logging.info(b)
        l.append(a)
        l.append(b)
        
        
#    logging.info(pl)

    

#    l =  sorted(students, key=attrgetter('surname','name')) 
#    l.append(FakeStudent())
    return l
