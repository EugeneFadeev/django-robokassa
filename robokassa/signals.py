# coding: utf-8
from __future__ import unicode_literals

from django.dispatch import Signal


result_received = Signal()
success_page_visited = Signal()
fail_page_visited = Signal()
