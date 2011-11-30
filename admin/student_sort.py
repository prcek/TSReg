# -*- coding: utf-8 -*-

from operator import attrgetter
import logging


cz_spec_dict = { u'Š':u'S', u'Ď':u'D', u'Č':u'C' }
cz_spec_dict = dict((ord(k), cz_spec_dict[k]) for k in cz_spec_dict)

def cz_spec_order(s):
    return s.translate(cz_spec_dict)


class FakeStudent():
    x_pair_empty_slot = True
    x_pair_no = 0
    x_pair_complete = False
    x_pair_first = False
    x_pair_second = True
    x_no = 0
    x_class_no = 0
    name = None
    surname = None
    def get_sex(self):
        return None 
 
    def key(self):
        return {'id':''} 

def get_single_sort():
        def g(obj):
            return (cz_spec_order(obj.surname),obj.name)
        return g

def get_school_sort():
        def g(obj):
            return (obj.school, obj.school_class, obj.addressing, cz_spec_order(obj.surname),obj.name)
        return g

def diffclass(s1,s2):
    if s1.school != s2.school:
        return True 
    if s1.school_class != s2.school_class:
        return True 
    if s1.addressing!= s2.addressing:
        return True 
 
    return False

def sort_students_kicked(students):
    return sort_students_single(students)

def sort_students_spare_single(students):
    return sort_students_single(students)

def sort_students_spare_school(students):
    return sort_students_school(students)

def sort_students_spare_pair(students):
    return sort_students_pair(students)

def sort_students_single(students):
    sl = sorted(students, key=get_single_sort()) 
    no = 0
    for s in sl:
        no+=1
        s.x_no = no
    return sl
 

def sort_students_school(students):
    sl = sorted(students, key=get_school_sort())
    cno = 0
    no = 0
    last_s = None 
    for s in sl:
        if (not last_s is None) and  diffclass(s,last_s):
            cno=0
        last_s = s
        cno+=1
        no+=1
        s.x_class_no = cno
        s.x_no = no

    return sl

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

    def get_compl():
        def g(obj):
            if (obj[0].x_pair_empty_slot or obj[1].x_pair_empty_slot):
                c=True
            else:
                c=False
            return (c,cz_spec_order(obj[0].surname),obj[0].name)
        return g


    pl = sorted(pl,key=get_compl())

    for (a,b) in pl:
        pno+=1
        a.x_pair_no = pno
        b.x_pair_no = pno
        l.append(a)
        l.append(b)
        
    no = 0
    for a in l:
        no+=1
        a.x_no = no

#    l =  sorted(l, key=get_compl()) 
#    l.append(FakeStudent())
    return l
