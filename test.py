import sys
import packet
import json
import pickle
import argparse

def main(argv):
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                       help='an integer for the accumulator')

main(sys.argv)