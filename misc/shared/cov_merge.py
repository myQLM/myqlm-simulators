#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author Alain Cady <alain.cady@atos.net>
@copyright 2015  Bull S.A.S.  -  All rights reserved.\n
           This is not Free or Open Source software.\n
           Please contact Bull SAS for details about its license.\n
           Bull - Rue Jean Jaurès - B.P. 68 - 78340 Les Clayes-sous-Bois
 cov_merge XML Coverage Merger
'''
from lxml import etree
from copy import deepcopy
import os

import argparse


def merge(to, *from_files):
    '''Do da job'''
    from_files = list(from_files)

    cov = etree.Element('coverage')
    sources = etree.Element('sources')
    source = etree.Element('source')
    source.text = os.getcwd()
    sources.append(source)
    cov.append(sources)
    packages = etree.Element('packages')
    cov.append(packages)

    while from_files:
        try:
            current = from_files.pop()
            with open(current, 'r') as currentXml:
                currentCov = etree.parse(currentXml)
            currentPakages = currentCov.xpath('/coverage/packages')[0]

            for p in currentPakages.getchildren():
                packages.append(deepcopy(p))
        except IOError as ioe:
            print '%s' % (ioe)

    with open(to, 'w') as destinationXML:
        destinationXML.write(etree.tostring(cov, pretty_print=True))

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('--output', '-o', help='Output File; %(default) if not specifyed',
                        default='merged.xml')
    PARSER.add_argument('input', nargs='+')

    ARGS = PARSER.parse_args()

    merge(ARGS.output, *ARGS.input)
