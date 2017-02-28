from __future__ import unicode_literals

import copy
import logging
import multiprocessing
import time
from importlib import import_module

from django.db import connection
from django.template.base import Node, NodeList
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from template_multiprocessing.utils import Process


CPU_COUNT = multiprocessing.cpu_count()
logger = logging.getLogger("django.template")


def NodeList_render(self, context):

    # First pass to see if multiprocessing is required for this nodelist. If
    # current process is already a daemon we can't use multiprocessing.
    has_multi = False
    if not multiprocessing.process.current_process()._daemonic:
        for node in self:
            if getattr(node, "__multiprocess_safe__", False):
                # Check predicate if any
                predicate = getattr(
                    node.__class__,
                    "__multiprocess_predicate__",
                    None
                )
                if predicate is not None:
                    if not predicate(node, context):
                        has_multi = False
                        break
                has_multi = True
                break

    # Original code if no multiprocessing required
    if not has_multi:
        bits = []
        for node in self:
            if isinstance(node, Node):
                bit = node.render_annotated(context)
            else:
                bit = node
            bits.append(force_text(bit))
        return mark_safe("".join(bits))

    # List of jobs that run on other cores
    jobs = []

    # The process queue
    queue = multiprocessing.Queue()

    # Queue that keeps track of how many cores are in use
    cores = multiprocessing.Queue(CPU_COUNT)

    # Synchronous queue
    squeue = []

    # Everything must go into a queue. Queue completion order is not fixed so
    # incorporate the index.
    expected_queue_size = 0
    for index, node in enumerate(self):
        if isinstance(node, Node):
            if getattr(node, "__multiprocess_safe__", False):
                p = Process(
                    target=self.render_annotated_multi,
                    args=(node, copy.deepcopy(context), index, queue, cores)
                )
                jobs.append(p)
                expected_queue_size += 1
            else:
                squeue.append((index, node))
        else:
            squeue.append((index, node))

    # Ensure we never run more than CPU_COUNT jobs on other cores.
    # Unfortunately multiprocessing.Pool doesn't work when used in classes so
    # roll our own.
    job_index = 0
    while queue.qsize() < expected_queue_size:
        # Use the cores queue to determine how many are free
        num_to_start = CPU_COUNT - cores.qsize()
        for i in range(num_to_start):
            if job_index < len(jobs):
                p = jobs[job_index]
                job_index += 1
                cores.put(1)
                p.daemon = True
                p.start()

        time.sleep(0.05)

    # Let the jobs complete
    for p in jobs:
        p.join()
        if p.exception:
            error, traceback = p.exception
            raise error

    # Empty the queue
    pipeline = {}
    while queue.qsize():
        index, rendered, callback, data = queue.get()
        pipeline[index] = (rendered, callback, data)
    for index, node in squeue:
        pipeline[index] = node

    # Call callbacks in non-threaded order
    indexes = sorted(pipeline.keys())
    bits = []
    for index in indexes:
        item = pipeline[index]
        if isinstance(item, Node):
            rendered = item.render_annotated(context)
        elif isinstance(item, tuple):
            rendered, callback, data = item
            if callback:
                module_name, func_name = callback.rsplit(".", 1)
                callback = getattr(import_module(module_name), func_name)
                callback(context.get("request"), data, last=index==indexes[-1])
        else:
            rendered = item
        bits.append(force_text(rendered))

    return mark_safe("".join(bits))


def NodeList_render_annotated_multi(self, node, context, index, queue, cores):
    result = ""
    try:
        # Multiprocess does a deepcopy of the process and this includes the
        # database connection. This causes issues because DB connection info is
        # recorded in thread locals. Close the DB connection - Django will
        # automatically re-establish it.
        connection.close()

        # Do the actual rendering
        result = node.render_annotated(context)

    finally:
        # Always put something on the queue
        data = {}
        try:
            callback_dotted_name = None
            callback = getattr(node, "__multiprocess_callback", None)
            if callback is not None:
                callback_dotted_name = callback.__module__ + "." \
                    + callback.func_name
            func = getattr(node, "__multiprocess_after_render", None)
            if func is not None:
                data = func(context)
        finally:
            queue.put((index, result, callback_dotted_name, data))

            # Signal a core is now available
            cores.get()


logger.info("template_multiprocessing patching django.template.base.NodeList")
NodeList.render = NodeList_render
NodeList.render_annotated_multi = NodeList_render_annotated_multi
