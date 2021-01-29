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


def process(url):
    '''
    Takes in an url and processes it into ansolute url and returns its soup.

    Input: 
        url: (str) url
    '''
    url = util.remove_fragment(url) 
    request = util.get_request(url)
    html = util.read_request(request)
    url = util.get_request_url(request)
    soup = bs4.BeautifulSoup(html, "html5lib")

    return url, soup


def parse(div_tags, index, course_map_filename):
    '''
    Parses through div tags with course info and updates the output index.

    Inputs:
        div_tags (bs4 ResultSet, lst): div tags with "courseblock main" or "courseblock subsequence" attribute
        index (dict): index to be updated
        course_map_filename: the json file that maps a course title to the identifier
    
    Returns:
        None
    '''
    regex = r'[a-zA-Z][-a-zA-Z0-9]*'
    regex_class = r'[\w-]+'
    classes = []

    for div_tag in div_tags:
        if div_tag.has_attr('class') and div_tag['class'][0] == 'courseblock':
            p_tags = div_tag.find_all("p")
            course = {}

            for p in p_tags:
                if p.has_attr('class'):
                    if p['class'][0] == "courseblocktitle":
                        title = re.findall(regex_class, p.text)
                        course['title'] = ' '.join([str(elem) for elem in title[:2]])
                        course['name'] = re.findall(regex, p.text)
                    elif p['class'][0] == "courseblockdesc":
                        desc = re.findall(regex_class, p.text)
                        course['desc'] = desc
            word_list = course['name'] + course['desc']

            if '-' in course['title']:
                parse_seq(course['title'], word_list, index, course_map_filename)
            else:
                course_id = course_identifier(course['title'], course_map_filename)
                update_index(course_id, word_list, index)
    



def course_identifier(course, course_map_filename):
    '''
    A fuinction that loads a json file and redirects course name 
    to its identifier.

    Inputs:
        course: (str) course title
        course_map_filename: json file
    
    Returns:
        course ID
    '''
    with open(course_map_filename) as f:
        data = json.load(f)
    return data[course]




def update_index(class_name, word_list, index):
    '''
    Updates the output index

    Inputs:
        word_list (lst): list of words from specific tag
        index (dict): index that will be updated
        class_name (str): name of the class
    
    Returns:
        None
    '''
    word_list = [word.lower() for word in word_list]
    for word in word_list:
        if word not in INDEX_IGNORE:
            if word not in index:
                index[word] = [class_name]
            else:
                if class_name not in index[word]:
                    index[word].append(class_name)


def parse_seq(class_name, word_list, index, course_map_filename):
    '''
    Function that will add each course in the sequence to the
    sequence descriptions.

    Inputs:
        class_name: name of sequence
        word_list: (str) words that appear in course description
        index: (dict) our index dict that we modify
        course_map_filename: JSON file that maps class name to IDs
    
    Returns: 
        None
    '''
    regex_seq = r'[a-zA-Z][-a-zA-Z0-9]+'
    seq = []
    seq_name = re.findall(regex_seq, class_name)
    dept = seq_name[0]
    for i, word in enumerate(seq_name):
        num = seq_name[i]
        if num.isnumeric():
            subsequence = dept + ' ' + num
            seq.append(subsequence)
    
    for course in seq:
        course_id = course_identifier(course, course_map_filename)
        update_index(course_id,word_list, index)


def process_links(parent_url, soup_links, processed_links, url_queue, count = 0, num_pages_to_crawl = 1000):
    '''
    Queues a link for processing and accounts for the processing of the URL

    Inputs:
        parent_url (str): URL to be processed
        soup_links (lst): list of <a> tags with embedded URL's
        processed_links (set): links that have already been processed
        url_queue (Queue object): queue of URL's ready to be parsed
        count (int): links that have been processed
        num_pages_to_crawl: the number of pages to process during the crawl
    
    Output:
        count (int): updated number of URL's that have been parsed and processed
    '''
    for link in soup_links:
        link = link.get('href')
        if link is not None:
            absolute_link = util.convert_if_relative_url(parent_url, link)
            
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
    count = 1
    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"


    url_queue = queue.Queue()

    # Parsing through starting_url for URL's and seeding url_queue

    parent_url, soup = process(starting_url)
    soup_links = soup.find_all("a")
    count = process_links(parent_url, soup_links, processed_links, url_queue, count = count)
    
    while not url_queue.empty():
        url = url_queue.get()
        parent_url, soup = process(url)

        links = soup.find_all("a")
        count = process_links(url, links, processed_links, url_queue, count = count)

        div_tags = soup.find_all("div")
        parse(div_tags, index)





if __name__ == "__main__":
    # usage = "python3 crawl.py <number of pages to crawl>"
    # args_len = len(sys.argv)
    #course_map_filename = "course_map.json"
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
    count = 1
    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    # Creating queue object to store URL's
    url_queue = queue.Queue()
    course_map_filename = "course_map.json"

    # Parsing through starting_url for URL's and seeding url_queue

    parent_url, soup = process(starting_url)
    soup_links = soup.find_all("a")
    count = process_links(parent_url, soup_links, processed_links, url_queue, count = count)
    

    while not url_queue.empty():
        url = url_queue.get()
        parent_url, soup = process(url)

        # Determining and appending course subsequence courses
        

        # Parsing through the webpage and processing URL's
        links = soup.find_all("a")
        count = process_links(url, links, processed_links, url_queue, count = count)

        div_tags = soup.find_all("div")
        parse(div_tags, index, course_map_filename)


    sorted_list = sorted(index.keys(), key=lambda x:x.lower())
    lines = []
    for ele in sorted_list:
        num_list = index[ele]
        for num in num_list:
            lines.append(str(num) + ' | ' + ele)

    with open('fileName.csv', 'w') as f:
        for line in lines:
            f.write(line + '\n')


