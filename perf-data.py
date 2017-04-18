#!/usr/bin/python2.7
# encoding: utf-8
import sys

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from argparse import FileType
from Analyzer import Analyzer
from Comparator import Comparator

def analyze(args):
    print "Inside analyze with args:"
    print 'Input Directory: {0}'.format(args.input_dir)
    print 'Output File: {0}'.format(args.output_file)
    lyzer = Analyzer()
    lyzer.loadResults(args.input_dir)
    lyzer.writeAnalysis(args.output_file)
    pass
def compare(args):
    print "Inside compare with args:"
    print 'First: {0}'.format(args.first)
    print 'Second: {0}'.format(args.second)
    compr = Comparator(args.first,args.second)
    return compr.compare()
    pass
def plot(args):
    print "Inside plot with args:"
    for file in args.summaries:    
        print 'File: {0}'.format(file) 
    pass

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)


    parser = ArgumentParser(prog="perf-data", formatter_class=RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(help="Sub-command Help")
    
    analyze_parser = subparsers.add_parser("analyze", help="Summarize a directory of performance regression output files")
    analyze_parser.add_argument("input_dir", help="Directory to process performance regression output files")
    analyze_parser.add_argument("output_file", help="File to output the summary information to (typicaly a json extension")
    analyze_parser.set_defaults(func=analyze)
    
    compare_parser = subparsers.add_parser("compare", help="Compare two summary files from previous summarize calls")
    compare_parser.add_argument("first", type=FileType('r'), help="Base summary file to use in comparison")
    compare_parser.add_argument("second", type=FileType('r'), help="Second summary file to compare against the first")
    compare_parser.set_defaults(func=compare)
    
    plot_parser = subparsers.add_parser("plot", help="Take a list of summary files and plot the results" )
    plot_parser.add_argument("summaries", nargs='+')
    plot_parser.set_defaults(func=plot)
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    args.func(args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
