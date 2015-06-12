#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import argparse
import mediajson

class DeepHarvest():

    ''' base class for all deep harvesting '''
    def __init__(self):
        pass

    def fetch_objects(self):
        pass

    def get_structure(self):
        pass

    def extract_metadata(self):
        pass

