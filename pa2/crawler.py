# CS122: Course Search Engine Part 1
#
# Zachary Yung, Corry Ke
#

import re
import util
import bs4
import queue
import json
import sys
import csv

INDEX_IGNORE = set(['a', 'also', 'an', 'and', 'are', 'as', 'at', 'be',
                    'but', 'by', 'course', 'for', 'from', 'how', 'i',
                    'ii', 'iii', 'in', 'include', 'is', 'not', 'of',
                    'on', 'or', 's', 'sequence', 'so', 'social', 'students',
                    'such', 'that', 'the', 'their', 'this', 'through', 'to',
                    'topics', 'units', 'we', 'were', 'which', 'will', 'with',
                    'yet'])

def process(parent_url, child_url):
    '''

    '''
    parent_url = util.remove_fragment(parent_url) # DO WE DO THIS BEFORE UTIL.CONVERT_IF_RELATIVE_URL OR AFTER
    child_url = util.remove_fragment(child_url)
    url = util.convert_if_relative_url(parent_url, child_url)
    request = util.get_request(url)
    html = util.read_request(request)
    soup = bs4.BeautifulSoup(html, "html5lib")

    return soup

def put_if(soup, count, num_pages_to_crawl):
    '''

    '''
    links = soup.find_all("a")
    for link in links:
        absolute_link = util.convert_if_relative_url(starting_url, link)
        if is_url_ok_to_follow(absolute_link, limiting_domain):
            if count < num_pages_to_crawl:
                url_queue.put(absolute_link)
                count += 1

def parse(soup, ):
    '''

    '''


def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generate a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping of
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index
    '''
    index = {}
    processed_links = []
    
    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    # Creating queue object to store URL's
    url_queue = queue.Queue()

    # Parsing through starting_url for URL's and seeding url_queue
    soup = process(starting_url, starting_url)
    links = soup.find_all("a")
    count = 1
    ###
    for link in links:
        link = link["href"]
        link = util.remove_fragment(link)
        absolute_link = util.convert_if_relative_url(starting_url, link)
        if util.is_url_ok_to_follow(absolute_link, limiting_domain):
            if count < num_pages_to_crawl and absolute_link not in processed_links:
                url_queue.put(absolute_link)
                processed_links.append(absolute_link)
                count += 1
            elif count == num_pages_to_crawl:
                break
        ###
    
    while not url_queue.empty():
        url = url_queue.get()
        request = util.get_request(url)
        html = util.read_request(request)
        soup = bs4.BeautifulSoup(html, "html5lib")

        div_tags = soup.find_all("div", class_="courseblock main")
        links = soup.find_all("a")

        ###
        for link in links:
            link = link["href"]
            link = util.remove_fragment(link)
            absolute_link = util.convert_if_relative_url(starting_url, link)
            if util.is_url_ok_to_follow(absolute_link, limiting_domain):
                if count < num_pages_to_crawl and absolute_link not in processed_links:
                    url_queue.put(absolute_link)
                    processed_links.append(absolute_link)
                    count += 1
                elif count == num_pages_to_crawl:
                    break
        ###

        if div_tags != []:
            for div_tag in div_tags:
                p_tags = div_tag.find_all("p")

                for p_tag in p_tags:
                    word_list = re.findall(regex, p_tag.text)

                    if p_tag.has_attribute("courseblocktitle"):
                        class_name = ' '.join([str(elem) for elem in string_list[:2]])

                    for word in word_list:
                        if word not in INDEX_IGNORE and word not in index:
                            index[word] = [class_name]
                        else:
                            index[word].append(class_name)

        # key_pair = ' '.join([str(elem) for elem in list]) where list is a list in the format ["ANTH", "20190"] and it turns it into "ANTH 20190"



    regex = r'\w+'
    string_list = re.findall(regex, string)


    # IGNORE
    if url_queue.empty():
        tags = soup.find_all("a")
        for tag in tags:
            url.queue.put(tag["href"])
    else:
        url = url_queue.get()
        request = util.get_request(url)
        html = util.read_request(request)
        soup = bs4.BeautifulSoup(html, "html5lib")
        tags = soup.find_all("a")
        for tag in tags:
            # Checking if URL is relative
            if not util.is_absolute_url(url):
                tag = util.convert_if_relative_url(url, tag)
            url_queue.put(tag["href"])

    # add seed
    # parse it
    # add children
    # pop it

    # dictionary
    # words within course titles
    # map a word to course identifier
    # if the word is already in the key of the dictionary, you add the value (course identifier) to the key that is already existing into a list

    # if the course is a subsequence, there is a list of the individual div tags that represent the sub-course and you have to parse through it 


    # is_url_ok_to_follow and if you've already been to url


if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)
        sys.exit(0)

    go(num_pages_to_crawl, course_map_filename, index_filename)
