import os
import sys
import re

from urllib.error import HTTPError
from urllib.parse import urlparse

import requests


def manage_domain_scheme(target_domain: str):
    # we need a function to add a scheme to the url is one if not present.
    # this regexp will check for a scheme
    scheme_regexp = re.compile(r'^https?://')

    mo = scheme_regexp.search(target_domain)
    # if no match is found, let's attach a default http:// scheme
    if mo is None:
        target_domain = "http://{domain}".format(domain=target_domain)

    return target_domain


def validate_web_url(url: str):

    try:
        # let's define a function to validate a url
        response = requests.get(url, allow_redirects=True)
        # if we dont get a 200 response, the url isn't valid
        if response.status_code != 200:

            raise Exception("Web-scraper error in vaidate_web_url fn url is {url}...error code: {errcode} error reason is: {errreason}\n".format(
                url=url, errcode=response.status_code, errreason=response.reason))

    except Exception as e:
        # lets return false to let the controller know its not a valid url
        print(e)
        return False
    else:
        return True


def format_path_as_file_location(link: str):
    # let's parse the url and grab the path
    parsed_url = urlparse(link)
    file_path = parsed_url.path

    # let's check to see if there is a path, or if the path is a backslash and rename it index
    if file_path == "/" or not file_path:
        file_path = "index"

    # next we need to strip away any leading or trailing slashes
    if file_path[0] == "/":
        file_path = file_path[1:]

    if file_path[-1] == "/":
        file_path = file_path[:-1]

    # if there is a slash anywhere in the path, let's split the string by the slashes and take the final pathname
    if "/" in file_path:
        file_pathList = file_path.split("/")
        file_path = file_pathList[-1]

    return file_path


def format_href_as_url(href: str, target_domain: str):

    # let's parse the target_domain to use it to format
    # an incorect href into a url
    parsed_target_domain = urlparse(target_domain)

    # if the href is "/", it's valid, but will need the scheme and domain
    if href != "/":
        # if its longer
        while href[0] == "/":
            # strip away any leading slashes
            href = href[1:]

        # we'll need a regexp to check for hrefs that arent valid
        # if there is a https:// or www. at the beginning, we'll need
        # to run some extra checks
        href_regexp = re.compile(
            r'((https?://)|(www.))(.*)+')

        mo = href_regexp.match(href)

        # we'll only return valid matchs from now on
        if mo:
            # let's asses for hrefs starting with either a www. or no scheme
            if mo.group() and re.match(r'www.', mo.group()) or mo.group() and not re.match(r'https?://', mo.group()):
                # if there wasn't shceme found
                href = "{scheme}://{href}".format(
                    scheme=parsed_target_domain.scheme, href=href)
                return href
            else:
                # if it has a scheme or domain, return it
                return href
        else:
            # there was no scheme or domain -> common in static websites
            href = "{scheme}://{net_location}/{href}".format(
                scheme=parsed_target_domain.scheme, net_location=parsed_target_domain.netloc, href=href)
            return href
    else:
        # if the href was "/", grab the scheme and target domain and prepend
        href = "{scheme}://{net_location}{href}".format(
            scheme=parsed_target_domain.scheme, net_location=parsed_target_domain.netloc, href=href)

        return href


def filter_pdf_link_locations(links: list):

    filtered_links = []

    for link in links:

        pdf_regexp = re.compile(r'.pdf$')

        mo = pdf_regexp.search(link)

        if mo is None:
            filtered_links.append(link)

    return filtered_links
