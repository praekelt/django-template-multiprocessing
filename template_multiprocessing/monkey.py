from __future__ import unicode_literals

import multiprocessing
import time

from django.db import connection
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


CPU_COUNT = multiprocessing.cpu_count()


def NodeList_render(self, context):

    # First pass to see if multiprocessing is required for this nodelist
    has_multi = False
    for node in self:
        if getattr(node, "__multiprocess_safe__", False):
            has_multi = True
            break

    # Original code is not multiprocessing required
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

    # Everything must go into a queue
    for index, node in enumerate(self):
        if isinstance(node, Node):
            if getattr(node, "__multiprocess_safe__", False):
                p = multiprocessing.Process(
                    target=self.render_annotated_multi,
                    args=(node, context, index, queue, cores)
                )
                jobs.append(p)
            else:
                queue.put((index, node.render_annotated(context)))
        else:
            queue.put((index, node))

    # Ensure we never run more than CPU_COUNT jobs on other cores.
    # Unfortunately multiprocessing.Pool doesn't work when used in classes so
    # roll our own.
    job_index = 0
    expected_queue_size = len(self)
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

    # Fetch the results from the queue and assemble
    bits = [None] * queue.qsize()
    while queue.qsize():
        tu = queue.get()
        bits[tu[0]] = force_text(tu[1])
    return mark_safe("".join(bits))

    def render_annotated_multi(self, node, context, index, queue, cores):
        # Multiprocess does a deepcopy of the process and this includes the
        # database connection. This causes issues because DB connection info is
        # recorded in thread locals. Close the DB connection - Django will
        # automatically re-establish it.
        connection.close()

        # Do the actual rendering
        queue.put((index, node.render_annotated(context)))

        # Signal a core is now available
        cores.get()
