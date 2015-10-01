"""
Simple scanner that checks for the existence of our generator tag
and a few other things.

It's slow and clunky, and it only scans one level beyond the root,
but it does the job.

Install:
pip --user -r requirements.txt

Run:
python awwnuts.py http://path/to/site
"""

import requests
import sys
from lxml import html
from optparse import OptionParser
from termcolor import colored
from subprocess import check_output
from subprocess import call

import time
from datetime import date


def check(url):
    page = requests.get(url)
    tree = html.fromstring(page.text)

    # check for pages that load, but show Foundry errors
    pre = tree.xpath("//pre")
    for text in pre:
        if "Type: foundry\exception" in text.text:
            return 0

    generator = tree.xpath("//meta[contains(@name,'generator')]/@content")

    # All generated pages have our generator tag, if it's not there then either the page didn't load
    # or it's quite messed up
    if not generator or not ('Gryphon' in generator[0]) or not ('Foundry' in generator[0]):
        return 0

    return 1


def main(base_url, opts):

    doScrapePage = False
    scrapeCommand = False

    if opts.webkit2png:
        ret = check_output(["which", "webkit2png"])
        if ret:
            doScrapePage = True
            today = date.today()
            scrapeCommand = "%s -F -D %s%d" % (ret.strip(), today.strftime("%Y-%m-%d-"), time.time())

    print colored("SCANNING %s" % base_url, 'green')
    sys.stdout.write("\n\n")

    page = requests.get(base_url)
    tree = html.fromstring(page.text)

    if not check(base_url):
        print colored('Failed to verify base URL', 'red')
        if doScrapePage:
            ret = check_output("%s %s" % (scrapeCommand, base_url), shell=True)

        exit(1)

    local_urls = tree.xpath("//a[starts-with(@href,'/')]/@href")
    scoped_urls = tree.xpath("//a[contains(@href,'%s')]/@href" % base_url)

    total = 0
    fails = 0
    for url in set(local_urls):
        total += 1
        # print url
        if not check(base_url + url):
            fails += 1
            print colored("FAIL %s%s" % (base_url, url), 'red')
            if doScrapePage:
                ret = check_output("%s %s%s" % (scrapeCommand, base_url, url), shell=True)
        else:
            print "%s %s%s" % (colored("Pass", 'green'), base_url, url)

    for url in set(scoped_urls):
        total += 1
        if not check(url):
            fails += 1
            print colored("FAIL %s" % url, 'red')
            if doScrapePage:
                ret = check_output("%s %s" % (scrapeCommand, url), shell=True)
        else:
            print "%s %s" % (colored("Pass", 'green'), url)

    sys.stdout.write("\n\n")
    print "Finished %s, %s" % (colored("%d total" % total, 'green'), colored("%d errors" % fails, 'red'))

if __name__ == "__main__":
    parser = OptionParser(version='%prog',
                          description="""Lookin for whoops.""")

    parser.add_option('-s', '--screenshot', dest='webkit2png', action="store_true",
                      help='If webkit2png is installed, screenshot failed pages')

    (options, args) = parser.parse_args()

    if not len(args):
        print colored("You must provide a URL", 'red')

    main(args[0], options)
