# dynamic links generator
'''
So i tried changing links in a template that had hundreds of em
I changed 4 links and got stressed out an started working on this project @dynalinks
'''


__author__ = 'Williams Usanga'

import bs4
import os
import os.path
from pprint import pprint

# let's get cracking :)


def open_file(fname, ftype="r"):
    with open(file, ftype) as contents:
        contents = contents.read()
    return contents


def remove_none_ascii(txt):
    return ''.join([i for i in txt if str(i).isascii()])


def dynamic_links(soup, tag, attr):
    links = soup.findAll(tag)

    for link in links:
        try:
            former_link = link[attr].strip('"\'').strip()

            # cases where
            # href = '#', 'javascript:void(0), javascript:;
            if former_link.lower() in ('#', 'javascript:void(0)', 'javascript:;') or former_link.startswith('javascript:') or former_link.startswith('{%'):
                continue # skip

            new_link = new_link_template.format(former_link)
            link[attr] = new_link
            # print(link)
        except KeyError:
            pass



file                = r'.\custom_admin\templates\custom_admin\student_home.html'
new_link_template   = """{{% static 'custom_admin/school_dashboard/www.einfosoft.com/templates/admin/smart/source/light/{}' %}}"""
folder, file_copy   = os.path.split(file)
filename, ext       = os.path.splitext(file_copy)
file_copy           = os.path.join(folder, filename + '_Copy' + ext)


soup                = bs4.BeautifulSoup(open_file(file, 'rb'), "html.parser")

dynamic_links(soup, 'link', 'href')
dynamic_links(soup, 'script', 'src')
dynamic_links(soup, 'img', 'src')
dynamic_links(soup, 'a', 'href')

html                = remove_none_ascii(str(soup.prettify()))


with open(file_copy, 'w') as file_copy:
    file_copy.write(html)

