# -*- coding: utf-8 -*-

from operator import attrgetter

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
    return sorted(students, key=attrgetter('surname','name')) 
