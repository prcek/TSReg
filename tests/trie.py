#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import sys
import os


class RevTrieXXXX:

    def __init__(self):
        self.root = [None, {}]


    def add(self, key, value):
         
        curr_node = self.root
        for ch in key[::-1]:
            curr_node = curr_node[1].setdefault(ch, [None, {}])
        curr_node[0] = value

    def find_max(self, key):
        curr_node = self.root
        prefix_len = 0
        for ch in key[::-1]:
            try:
                curr_node = curr_node[1][ch]
                prefix_len+=1
            except KeyError:
                if curr_node == self.root:
                    return (0,None)
                break

        while curr_node[0] is None:
            curr_node = curr_node[1].itervalues().next()
 
        return (prefix_len,curr_node[0])


    def __str__(self):
        return self.root.__str__()


class InfTrie:
    def __init__(self):
        self.root = [None, {}]

    def add(self, pattern, proposal):
        curr_node = self.root
        for ch in pattern[::-1]:
            curr_node = curr_node[1].setdefault(ch, [None, {}])
        curr_node[0] = (pattern,proposal)

    def find_max(self, key):
        curr_node = self.root
        prefix_len = 0
        for ch in key[::-1]:
            try:
                curr_node = curr_node[1][ch]
                prefix_len+=1
            except KeyError:
                if curr_node == self.root:
                    return (0,None)
                break

        while curr_node[0] is None:
            curr_node = curr_node[1].itervalues().next()
 
        return (prefix_len,curr_node[0])


    def do(self,text,default=None):
        (suffix_len, rule) = self.find_max(text)
        if suffix_len == 0:
            return default 


        pattern = rule[0]
        proposal = rule[1]

        if text == pattern:
            return proposal

        base = text[:-suffix_len]
        pattern_base = pattern[:-suffix_len]
        prefix_len = len(pattern_base) 
        proposal_suffix = proposal[prefix_len:]
        return base+proposal_suffix
        



if __name__ == "__main__":    

    from inflect_data import INFLECT_PATTERNS

    t = InfTrie()

    for p in INFLECT_PATTERNS:
        t.add(p[2],p[3])



    print t.do(u"Test")
    print t.do(u"Lucie")
    print t.do(u"Honza")
    print t.do(u"Španěl")
    print t.do(u"Jiří")
    print t.do(u"Novák")
    print t.do(u"Bůček")
    print t.do(u"X")

#    t.add(u"foo", "A")
#    t.add(u"foik34895ěščáíěšřýá", "B")
#    t.add(u"lba", "C")

#    print t.find_max('fuc') 
#    print t.find_max('lba') 
#    print t.find_max('pako') 

    print "Ok."

