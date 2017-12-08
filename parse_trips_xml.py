#!/usr/bin/env python
#-*-coding: utf-8 -*-

import argparse
import os
import re
import xml.etree.ElementTree as ET
import time


def get_clean_parse(file):
    try:
        test_pattern = a.split("<rdf:RDF")[1].split("</terms>")[0]
        rdf_pattern = "<rdf:RDF" + test_pattern
    except IndexError:
        out = file.split("/")[-1] + "\n"
        error.write(out)
        return
    
    pattern = re.compile(r' input=".+\n')
    if pattern.search(a):
        TEXT = "\n     <TEXT> " + \
            a.split("input=\"")[1].split('\n"')[0] + "</TEXT>"

    # not very efficient but quickly done, change later so don't have to
    # create a file for intermediate processing
    file = file + ".rdf"
    with open(file, 'w') as g:
        g.write(rdf_pattern)

    file_name = file
    tree = ET.parse(file_name)
    root = tree.getroot()
    os.remove(file)

    relation_id = 0

# GET NUMBER OF CHUNKS/WORDS EXPRESSED BY <rdf> TAG IN TRIPS XML
    i = 0
    for child in root:
        i += 1

    rootchunkitem = 0
    while rootchunkitem < len(root[0]):
        if root[0][rootchunkitem].tag.split("}")[1] == 'start':
            startval = "start=" + root[0][rootchunkitem].text
        elif root[0][rootchunkitem].tag.split("}")[1] == 'end':
            endval = "end=" + root[0][rootchunkitem].text
        rootchunkitem += 1

    myparse = "\n<SENTENCE id=" + \
        root[0].attrib.values()[0] + " " + startval + " " + endval + ">" + TEXT

    chunk_id = {}
    n = 0
    while n < i:
        k = len(root[n])  # NUMBER OF INFO LINES IN EACH <rdf> CHUNK
        chunk_id[n] = root[n].attrib.values()[0]

        dic_tag = {}
        dic_text = {}

        p = 2  # starting with 2 as index 0 and 1 are always going to be there - indicator and type

        while p <= k - 1:
            dic_tag[str(p)] = str(root[n][p].tag.split("}")[1])

            if root[n][p].tag.split("}")[1] == 'start' or root[n][p].tag.split("}")[
                    1] == 'end':
                dic_text[str(p)] = str(p)
            else:
                if root[n][p].text is None:
                    mylist = (root[n][p].attrib.values())
                    dic_text[str(p)] = str(str(mylist).strip("'[").strip("]'"))
                else:
                    dic_text[str(p)] = str(root[n][p].text)
            p += 1

        lf_list = []
        role_list = []

        for key, value in dic_text.items():
            if "#" not in value:
                lf_list.append(key)
            else:
                role_list.append(key)

        myparse += "\n     " + "<PHRASE" + " id=" + \
            chunk_id[n] + " type=" + root[n][1].text + " " + root[n][0].tag.split("}")[1] + "=" + root[n][0].text

        for lf in lf_list:
            if root[n][int(lf)].tag.split("}")[1] == 'start':
                startval = "start=" + root[n][int(lf)].text
            elif root[n][int(lf)].tag.split("}")[1] == 'end':
                endval = "end=" + root[n][int(lf)].text
            if (root[n][int(lf)].tag.split("}")[1] != 'start') and (
                    root[n][int(lf)].tag.split("}")[1] != 'end'):
                myparse += " " + \
                    root[n][int(lf)].tag.split("}")[1] + "=" + root[n][int(lf)].text
        myparse += " " + startval + " " + endval + ">"

        for role in role_list:
            relation_id += 1
            myparse += "\n     " + "<RELATION id=" + \
                str(relation_id) + " head=" + chunk_id[n] + " " + "res=" + dic_text[role].split("#")[1] + " label=" + dic_tag[role] + ">"

        n += 1
    myparse += "\n</SENTENCE>\n\n"

    with open(file.split(".rdf")[0] + '.clean', 'w') as new:
        new.write(myparse)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This is a script to create cleaner/simpler XMLs from the TRIPS XML output.')
    parser.add_argument(
        "--path",
        dest="path",
        required=True,
        help='path to the input directory containing all TRIPS XML parses')
    args = parser.parse_args()

    with open(time.strftime("%Y%m%d-%H%M") + '.err', 'a') as error:
     error.write("The following files did not have a parse.\n\n")
     for dir in os.listdir(args.path):
        if dir.startswith("batch"):
            dir = os.path.join(args.path, dir)
            for file in os.listdir(dir):
                if file.endswith(".xml"):
                    with open(os.path.join(args.path, dir, file), 'r') as f:
                        a = f.read()
                        get_clean_parse(os.path.join(input, dir, file))
    print "********************\nCleaned parses are in the same directory as the original parse files.\n\nFile %s in the current directory contains the list of files that did not have parses to be cleaned.\n********************\n" % str(error).split("'")[1]
