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
    return url

def request(url):
    request = util.get_request(url)
    html = util.read_request(request)
    soup = bs4.BeautifulSoup(html, "html5lib")
    return soup


def parse(courseblockmains, index):
    '''
    
    '''
    regex = r'[\w-]+'

    for div_tag in courseblockmains:
        p_tags = div_tag.find_all("p")
        for p_tag in p_tags:
            if p_tag.has_attr('class') and (p_tag['class'][0] == 'courseblocktitle' or p_tag['class'][0] == 'courseblock subsequence'):
                word_list = re.findall(regex, p_tag.text)
                class_name = ' '.join([str(elem) for elem in word_list[:2]])
                if '-' in class_name:
                    parse_seq(class_name, word_list, index)
                    continue

                update_index(word_list, index, class_name)

def update_index(word_list, index, class_name):
    for word in word_list:
        if word in INDEX_IGNORE:
            continue
        if word not in index:
            index[word] = [class_name]
        else:
            index[word].append(class_name)


def parse_seq(class_name, word_list, index):
    regex_seq = r'\w+'
    seq = []
    seq_name = re.findall(regex_seq, class_name)
    dept = seq_name[0]
    for i, word in enumerate(seq_name):
        num = seq_name[i]
        if num.isnumeric():
            subsequence = dept + '' + num
            seq.append(subsequence)
    
    for course in seq:
        update_index(word_list, index, course)


def process_links(parent_url, soup_links, processed_links, url_queue, count = 0, num_pages_to_crawl = 1000):
    for link in soup_links:
        link = link.get('href')
        if link is not None:
            absolute_link = process(parent_url, link)
            link = util.remove_fragment(link)
            
            if util.is_url_ok_to_follow(absolute_link, limiting_domain):
                if count < num_pages_to_crawl and absolute_link not in processed_links:
                    url_queue.put(absolute_link)
                    processed_links.add(absolute_link)
                    count += 1
                elif count == num_pages_to_crawl:
                    break

    return count


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
    processed_links = set()
    
    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    # Creating queue object to store URL's
    url_queue = queue.Queue()

    # Parsing through starting_url for URL's and seeding url_queue
    parent_url = process(starting_url, starting_url)
    soup = request(parent_url)
    links = soup.find_all("a")
    count = process_links(parent_url, links, processed_links, url_queue)
    
    while not url_queue.empty():
        url = url_queue.get()
        soup = request(url)

        div_tags = soup.find_all("div", class_="courseblock main")
        links = soup.find_all("a")
        count = process_links(url, links, processed_links, url_queue, count = count)

        if div_tags != []:
            parse(div_tags, index)

       



    


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
    # usage = "python3 crawl.py <number of pages to crawl>"
    # args_len = len(sys.argv)
    # course_map_filename = "course_map.json"
    # index_filename = "catalog_index.csv"
    # if args_len == 1:
    #     num_pages_to_crawl = 1000
    # elif args_len == 2:
    #     try:
    #         num_pages_to_crawl = int(sys.argv[1])
    #     except ValueError:
    #         print(usage)
    #         sys.exit(0)
    # else:
    #     print(usage)
    #     sys.exit(0)

    # go(num_pages_to_crawl, course_map_filename, index_filename)
    index = {}
    processed_links = set()
    
    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    
    url_queue = queue.Queue()

    parent_url = process(starting_url, starting_url)
    soup = request(parent_url)
    links = soup.find_all("a")
    count = process_links(parent_url, links, processed_links, url_queue)
    
    while not url_queue.empty():
        url = url_queue.get()
        soup = request(url)

        div_tags = soup.find_all("div", class_="courseblock main")
        links = soup.find_all("a")
        count = process_links(url, links, processed_links, url_queue, count = count)

        if div_tags != []:
            parse(div_tags, index)

    
    print(index)

    #THINGS TO DO: Make sure we go through Coursedesc too when parsing. Need to map courses to identifier when done. 
    #If you want to see what index looks like, type python3 crawler.py in your terminal. Takes <2 min to run. 