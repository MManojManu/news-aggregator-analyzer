from django import template
from django.conf import settings

register = template.Library()

LEADING_PAGE_RANGE_DISPLAYED = getattr(settings, "LEADING_PAGE_RANGE_DISPLAYED", 5)
TRAILING_PAGE_RANGE_DISPLAYED = getattr(settings, "TRAILING_PAGE_RANGE_DISPLAYED", 5)
LEADING_PAGE_RANGE = getattr(settings, "LEADING_PAGE_RANGE", 4)
TRAILING_PAGE_RANGE = getattr(settings, "TRAILING_PAGE_RANGE", 4)
NUM_PAGES_OUTSIDE_RANGE = getattr(settings, "NUM_PAGES_OUTSIDE_RANGE", 2)
ADJACENT_PAGES = getattr(settings, "NUM_PAGES_OUTSIDE_RANGE", 2)


@register.inclusion_tag('_paginator.html')
def get_paginator(paginator, page_obj):
    pages_outside_leading_range = pages_outside_trailing_range = range(0)
    in_leading_range = in_trailing_range = False
    if page_obj.paginator.num_pages <= LEADING_PAGE_RANGE_DISPLAYED:
        in_leading_range = in_trailing_range = True
        page_numbers = [n for n in range(1, page_obj.paginator.num_pages + 1) if
                        n > 0 and n <= page_obj.paginator.num_pages]
    elif page_obj.number <= LEADING_PAGE_RANGE:
        in_leading_range = True
        page_numbers = [n for n in range(1, LEADING_PAGE_RANGE_DISPLAYED + 1) if
                        n > 0 and n <= page_obj.paginator.num_pages]
        pages_outside_leading_range = [n + page_obj.paginator.num_pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
    elif (page_obj.number > page_obj.paginator.num_pages - TRAILING_PAGE_RANGE):
        in_trailing_range = True
        page_numbers = [n for n in range(page_obj.paginator.num_pages - TRAILING_PAGE_RANGE_DISPLAYED + 1,
                                         page_obj.paginator.num_pages + 1) if
                        n > 0 and n <= page_obj.paginator.num_pages]
        pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]
    else:
        page_numbers = [n for n in range(page_obj.number - ADJACENT_PAGES, page_obj.number + ADJACENT_PAGES + 1) if
                        n > 0 and n <= page_obj.paginator.num_pages]
        pages_outside_leading_range = [n + page_obj.paginator.num_pages for n in range(0, -NUM_PAGES_OUTSIDE_RANGE, -1)]
        pages_outside_trailing_range = [n + 1 for n in range(0, NUM_PAGES_OUTSIDE_RANGE)]

    return {
        'page_numbers': page_numbers,
        'pages_outside_leading_range': pages_outside_leading_range,
        'pages_outside_trailing_range': pages_outside_trailing_range,
        'paginator': paginator,
        'page_obj': page_obj,
        'in_leading_range': in_leading_range,
        'in_trailing_range': in_trailing_range,
    }
