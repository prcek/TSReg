#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import sys
import os


class RevTrie:

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
        self.rt = RevTrie()     

    def add(self, pattern, proposal):
        self.rt.add(pattern,(pattern,proposal))

    def do(self,text):

#        String inft_p = best_m.getPatern();
#        String inft_t = best_m.getInflected();
#
#        String base = text.substring(0,text.length()-best_v);
#        if ((inft_p.length()-best_v)<0) return "";
#        if ((inft_p.length()-best_v)>=inft_t.length()) return base;
#        String addon = inft_t.substring(inft_p.length()-best_v);
#        return base+addon;
        return text



if __name__ == "__main__":    
    t = RevTrie()
    t.add(u"foo", "A")
    t.add(u"foik34895ěščáíěšřýá", "B")
    t.add(u"lba", "C")

    print t.find_max('fuc') 
    print t.find_max('lba') 
    print t.find_max('pako') 

    print "Ok."

