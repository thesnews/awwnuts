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


def check(url):
    page = requests.get(url)
    tree = html.fromstring(page.text)
    generator = tree.xpath("//meta[contains(@name,'generator')]/@content")

    if not generator or not ('Gryphon' in generator[0]) or not ('Foundry' in generator[0]):
        return 0
    else:
        return 1


def main(base_url, opts):
    print colored("SCANNING %s" % base_url, 'green')
    sys.stdout.write("\n\n")

    page = requests.get(base_url)
    tree = html.fromstring(page.text)

    if not check(base_url):
        print colored('Unable to load base URL', 'red')
        exit(1)

    local_urls = tree.xpath("//a[starts-with(@href,'/')]/@href")
    scoped_urls = tree.xpath("//a[contains(@href,'%s')]/@href" % base_url)

    for url in set(local_urls):
        # print url
        sys.stdout.write("Checking %s%s " % (base_url, url))
        if not check(base_url + url):
            print colored("Fail", 'red')
        else:
            print colored("Pass", "green")

    for url in set(scoped_urls):
        sys.stdout.write("Checking %s " % (url))
        if not check(url):
            print colored("Fail", 'red')
        else:
            print colored("Pass", "green")


if __name__ == "__main__":
    parser = OptionParser(version='%prog',
                          description="""Lookin for whoops.""")

    parser.add_option('-x', '--ignore', dest='ignore', type='string',
                      action='append', help='Ignore files or folders')

    (options, args) = parser.parse_args()

    if not len(args):
        print colored("You must provide a URL", 'red')

    main(args[0], options)
