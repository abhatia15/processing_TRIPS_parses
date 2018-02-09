#!/usr/bin/env python
#-*-coding: utf-8 -*-

import argparse
import os
import re
import xml.etree.cElementTree as ET
import time
import pandas as pd
import numpy as np

d = {}

def get_clean_parse(file):
    try:
        new_rdf_pattern = ""
        relevant_rdf_pattern = a.split("<rdf:Description")[1:]
        for item in relevant_rdf_pattern:
            individual_rdf = item.split("</rdf:Description>")[0]
            new_rdf_pattern += "  <rdf:Description" + individual_rdf + "</rdf:Description>\n"
        root_pattern = a.split("<rdf:RDF")[1].split("<rdf:Description")[0]
        rdf_pattern = "<rdf:RDF  " + root_pattern + new_rdf_pattern + "</rdf:RDF>"
    except IndexError:
        out = file.split("/")[-1] + "\n"
        error.write(out)
        return
    
    pattern = re.compile(r' input=".+\n')
    if pattern.search(a):
        get_clean_parse.TEXT = a.split("input=\"")[1].split('\n"')[0].split(">")[0].split(".")[0] + "."


def refine_cleaned_parse(f):
    with open(f, 'r') as g:
        a = g.read()
        get_clean_parse(f)
    print f

    h = f + ".clean"
    tree = ET.ElementTree(file=h)
    root = tree.getroot()
    root.attrib['text'] = get_clean_parse.TEXT

    pi = 0
    ri = 0
    for child in root:
        if child.tag != "TEXT":
            if child.tag == "PHRASE":
                pi += 1
                child.tag = child.tag + str(pi)
                d[child.tag] = child.attrib
            elif child.tag == "RELATION":
                ri += 1
                child.tag = child.tag + str(ri)
                d[child.tag] = child.attrib
    print "\n"
    d[root.tag] = root.attrib
    df = pd.DataFrame(data=d)
    df = df.T


########################################################################################
######## Get sentence's start and end points as well as its text. We need to add #######
######## sentence's text to the SA phrase- we can identify it using the index and ######
######## indicator information. It should also have the same start and end points.######
########################################################################################
    sent_start = df.ix['SENTENCE', 'start']
    sent_end = df.ix['SENTENCE', 'end']
    sent_text = df.ix['SENTENCE', 'text']


########################################################################################
########Change span for root word. Find root word by finding the phrase with same start and end as sentence's, but it already has text in its text column instead of NaN. To find the span of the relevant word (note the word may be used in a sentence multiple times, we need to find the span for the one that is used as the root), TODO: we need to make sure we find spans for all usages of the word in the sentence and use the span that is not already mentioned for that word. Also the spans mentioned in the XML are not thrown away, they are renamed as tripsstart and tripsend respectively. This is to make sure we don't lose info about the root word in the sentence that the TRIPS XML parse provides to us.
########################################################################################
    idx_root = df[(df['start'] == sent_start) & (df['end'] == sent_end) & (df['indicator'] != "SPEECHACT") & (df['text'] != sent_text)]

#######################################################################################
### ADD SPANS FOR THE ACTUAL WORDS HERE ###############################################
### TODO: MAKE SURE THE SPAN IS ADDED FOR THE CORRECT ONE AS THERE MAY BE REPEATED WORDS
#######################################################################################
    length = len(idx_root)
    i = 0
    for i in range(length):
        idx_root_text = df.ix[idx_root.index[i]]['text']
        if str(idx_root_text) != "nan":
            etext = re.compile(idx_root_text.lower())
            for m in etext.finditer(str(sent_text)):
                textstart = m.start()
                textend = m.end()
            df.ix[idx_root.index[i]]['start'] = textstart
            df.ix[idx_root.index[i]]['end'] = textend
        elif 'OPERATOR' in df.columns:
            idx_root_operator = df.ix[idx_root.index[i]]['OPERATOR']
            print "*****idx_root_operator: ", idx_root_operator
            if str(idx_root_operator) != "nan":
                otext = re.compile(idx_root_operator.lower())
                for m in otext.finditer(str(sent_text)):
                    operatorstart = m.start()
                    operatorend = m.end()
                df.ix[idx_root.index[i]]['start'] = operatorstart
                df.ix[idx_root.index[i]]['end'] = operatorend
        else:
            print "\nThe following case is not covered.\n" #in case there are other cases that we did not realize and did not cover above
            print df.ix[idx_root.index[i]]


########################################################################################
######## Find row for the relevant SA phrase- it has the same start and end points as sentence and has SPEECHACT as indicator. Find its index.
########################################################################################
    idx = df[((df['start'] == sent_start) & (df['end'] == sent_end) & (df['indicator'] == "SPEECHACT"))].index[0] #getting the fist one for which condition is true, it should be the only one though in our data. But have not checked for that yet if that is indeed true.
    df.ix[idx]['text'] = sent_text


########################################################################
### Convert dataframe back into the XML format. ########################
########################################################################
    parse = "<SENTENCE id=\"" + df.ix['SENTENCE', 'id'] + "\" start=\"" + df.ix['SENTENCE', 'start'] + "\" end=\"" + df.ix['SENTENCE', 'end'] + "\">\n    <TEXT> \"" + sent_text + "\n\"</TEXT>"

    r = re.compile("([a-zA-Z]+)([0-9]+)")
    for item in df.index:
        if item != "SENTENCE":
            n = r.match(item).group(1)
            parse = parse + "\n    <" + n
            parse = parse + " id=\"" + df.ix[item, 'id'] + "\""
            if n == "PHRASE":
                parse = parse + " type=\"" + df.ix[item, 'type']  + "\""
                parse = parse + " indicator=\"" + df.ix[item, 'indicator'] + "\""
                if str(df.ix[item, 'PUNCTYPE']) != "nan":
                    parse = parse + " PUNCTYPE=\"" + df.ix[item, 'PUNCTYPE'] + "\""
                if ('OPERATOR' in df.columns) and (str(df.ix[item, 'OPERATOR']) != "nan"):
                    parse = parse + " OPERATOR=\"" + df.ix[item, 'OPERATOR'] + "\""
                if ('VALUE' in df.columns) and (str(df.ix[item, 'VALUE']) != "nan"):
                    parse = parse + " VALUE=\"" + df.ix[item, 'VALUE'] + "\""
                if ('SCALE' in df.columns) and (str(df.ix[item, 'SCALE']) != "nan"):
                    parse = parse + " SCALE=\"" + df.ix[item, 'SCALE'] + "\""
                if ('WNSENSE' in df.columns) and (str(df.ix[item, 'WNSENSE']) != "nan"):
                    parse = parse + " WNSENSE=\"" + df.ix[item, 'WNSENSE'] + "\""
                if ('NAME-OF' in df.columns) and (str(df.ix[item, 'NAME-OF']) != "nan"):
                    parse = parse + " NAME-OF=\"" + df.ix[item, 'NAME-OF'] + "\""
                if ('VFORM' in df.columns) and (str(df.ix[item, 'VFORM']) != "nan"):
                    parse = parse + " VFORM=\"" + df.ix[item, 'VFORM'] + "\""
                if ('HOUR' in df.columns) and (str(df.ix[item, 'HOUR']) != "nan"):
                    parse = parse + " HOUR=\"" + df.ix[item, 'HOUR'] + "\""
                if ('PROFORM' in df.columns) and (str(df.ix[item, 'PROFORM']) != "nan"):
                    parse = parse + " PROFORM=\"" + df.ix[item, 'PROFORM'] + "\""
                if ('PROGR' in df.columns) and (str(df.ix[item, 'PROGR']) != "nan"):
                    parse = parse + " PROGR=\"" + df.ix[item, 'PROGR'] + "\""
                if ('TENSE' in df.columns) and (str(df.ix[item, 'TENSE']) != "nan"):
                    parse = parse + " TENSE=\"" + df.ix[item, 'TENSE'] + "\""
                if ('SIZE' in df.columns) and (str(df.ix[item, 'SIZE']) != "nan"):
                    parse = parse + " SIZE=\"" + df.ix[item, 'SIZE'] + "\""
                if ('INTENSITY' in df.columns) and (str(df.ix[item, 'INTENSITY']) != "nan"):
                    parse = parse + " INTENSITY=\"" + df.ix[item, 'INTENSITY'] + "\""
                if ('QUAN' in df.columns) and (str(df.ix[item, 'QUAN']) != "nan"):
                    parse = parse + " QUAN=\"" + df.ix[item, 'QUAN'] + "\""
                if ('ORIENTATION' in df.columns) and (str(df.ix[item, 'ORIENTATION']) != "nan"):
                    parse = parse + " ORIENTATION=\"" + df.ix[item, 'ORIENTATION'] + "\""
                if str(df.ix[item, 'text']) != "nan":
                    parse = parse + " text=\"" + df.ix[item, 'text'] + "\""
                parse = parse + " start=\"" + str(df.ix[item, 'start']) + "\""
                parse = parse + " end=\"" + str(df.ix[item, 'end']) + "\"/>"
            elif n == "RELATION":
                parse = parse + " head=\"" + df.ix[item, 'head']  + "\""
                parse = parse + " res=\"" + df.ix[item, 'res']  + "\""
                parse = parse + " label=\"" + df.ix[item, 'label']  + "\"/>"

    parse = parse + "\n</SENTENCE>"

    with open(f.split(".rdf")[0] + '.clean2', 'w') as new:
        new.write(parse)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This is a script to clean the simpler XMLs previously created from the TRIPS XML output.')
    parser.add_argument(
        "--path",
        dest="path",
        required=True,
        help='path to the input directory containing all TRIPS original as well as cleaned XML parses')
    args = parser.parse_args()

    with open(time.strftime("%Y%m%d-%H%M") + '.err', 'a') as error:
        error.write("The following files did not have a parse.\n\n")
        for dir in os.listdir(args.path):
            if dir.startswith("batch"):
                dir = os.path.join(args.path, dir)
                for file in os.listdir(dir):
                    if file.endswith(".xml"):
                        try:
                            with open(os.path.join(args.path, dir, file), 'r') as f:
                                a = f.read()
                                refine_cleaned_parse(os.path.join(input, dir, file))
                        except:
                            print 'error'
    print "********************\nCleaned parses are in the same directory as the original parse files.\n\nFile %s in the current directory contains the list of files that did not have parses to be cleaned.\n********************\n" % str(error).split("'")[1]


########################################################################
### TODO: add this cleaned XML into the scenes files. ##################
########################################################################


