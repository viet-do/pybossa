# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2013 SF Isle of Man Limited
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa.  If not, see <http://www.gnu.org/licenses/>.

from StringIO import StringIO
import json
import requests
from flask.ext.babel import gettext
from pybossa.util import unicode_csv_reader
from pybossa.model.task import Task
from pybossa.cache import apps as cached_apps


class BulkImportException(Exception):
    pass


def variants():
    """Returns all the importers and variants defined within this module"""
    variants = [cls.variants() for cls in _importers.values()]
    variants = [item for sublist in variants for item in sublist]
    return variants


def create_importer_for(template):
    return _importers[template]()


class _BulkTaskImport(object):
    importer_id = None

    @classmethod
    def variants(self):
        return [self.importer_id] if self.importer_id != None else []

    def tasks(self, form):
        """Returns a generator with all the tasks imported"""
        pass

    def _import_csv_tasks(self, csvreader):
        headers = []
        data_rows_present = False
        fields = set(['state', 'quorum', 'calibration', 'priority_0',
                      'n_answers'])
        field_header_index = []

        for row in csvreader:
            if not headers:
                headers = row
                if len(headers) != len(set(headers)):
                    msg = gettext('The file you uploaded has '
                                  'two headers with the same name.')
                    raise BulkImportException(msg)
                field_headers = set(headers) & fields
                for field in field_headers:
                    field_header_index.append(headers.index(field))
            else:
                data_rows_present = True
                task_data = {"info": {}}
                for idx, cell in enumerate(row):
                    if idx in field_header_index:
                        task_data[headers[idx]] = cell
                    else:
                        task_data["info"][headers[idx]] = cell
                yield task_data
        if data_rows_present is False:
            raise BulkImportException(gettext('Oops! It looks like the file is empty.'))

    def _get_csv_data_from_request(self, r):
        if r.status_code == 403:
            msg = "Oops! It looks like you don't have permission to access" \
                " that file"
            raise BulkImportException(gettext(msg), 'error')
        if ((not 'text/plain' in r.headers['content-type']) and
                (not 'text/csv' in r.headers['content-type'])):
            msg = gettext("Oops! That file doesn't look like the right file.")
            raise BulkImportException(msg, 'error')

        csvcontent = StringIO(r.text)
        csvreader = unicode_csv_reader(csvcontent)
        return self._import_csv_tasks(csvreader)


class _BulkTaskCSVImport(_BulkTaskImport):
    importer_id = "csv"

    def tasks(self, form):
        dataurl = self._get_data_url(form)
        r = requests.get(dataurl)
        return self._get_csv_data_from_request(r)

    def _get_data_url(self, form):
        return form.csv_url.data


class _BulkTaskGDImport(_BulkTaskImport):
    importer_id = "gdocs"
    googledocs_urls = {
        'spreadsheet': None,
        'image': "https://docs.google.com/spreadsheet/ccc"
                 "?key=0AsNlt0WgPAHwdHFEN29mZUF0czJWMUhIejF6dWZXdkE"
                 "&usp=sharing",
        'sound': "https://docs.google.com/spreadsheet/ccc"
                 "?key=0AsNlt0WgPAHwdEczcWduOXRUb1JUc1VGMmJtc2xXaXc"
                 "&usp=sharing",
        'video': "https://docs.google.com/spreadsheet/ccc"
                 "?key=0AsNlt0WgPAHwdGZ2UGhxSTJjQl9YNVhfUVhGRUdoRWc"
                 "&usp=sharing",
        'map': "https://docs.google.com/spreadsheet/ccc"
               "?key=0AsNlt0WgPAHwdGZnbjdwcnhKRVNlN1dGXy0tTnNWWXc"
               "&usp=sharing",
        'pdf': "https://docs.google.com/spreadsheet/ccc"
               "?key=0AsNlt0WgPAHwdEVVamc0R0hrcjlGdXRaUXlqRXlJMEE"
               "&usp=sharing"}

    @classmethod
    def variants(self):
        return [("-".join([self.importer_id, mode]))
                for mode in self.googledocs_urls.keys()]

    def tasks(self, form):
        dataurl = self._get_data_url(form)
        r = requests.get(dataurl)
        return self._get_csv_data_from_request(r)

    def _get_data_url(self, form):
        # For old data links of Google Spreadsheets
        if 'ccc?key' in form.googledocs_url.data:
            return ''.join([form.googledocs_url.data, '&output=csv'])
        # New data format for Google Drive import is like this: 
        # https://docs.google.com/spreadsheets/d/key/edit?usp=sharing
        else:
            return ''.join([form.googledocs_url.data.split('edit')[0], 
                            'export?format=csv'])


class _BulkTaskEpiCollectPlusImport(_BulkTaskImport):
    importer_id = "epicollect"

    def tasks(self, form):
        dataurl = self._get_data_url(form)
        r = requests.get(dataurl)
        return self._get_epicollect_data_from_request(r)

    def _import_epicollect_tasks(self, data):
        for d in data:
            yield {"info": d}

    def _get_data_url(self, form):
        return 'http://plus.epicollect.net/%s/%s.json' % \
            (form.epicollect_project.data, form.epicollect_form.data)

    def _get_epicollect_data_from_request(self, r):
        if r.status_code == 403:
            msg = "Oops! It looks like you don't have permission to access" \
                " the EpiCollect Plus project"
            raise BulkImportException(gettext(msg), 'error')
        if not 'application/json' in r.headers['content-type']:
            msg = "Oops! That project and form do not look like the right one."
            raise BulkImportException(gettext(msg), 'error')
        return self._import_epicollect_tasks(json.loads(r.text))


def create_tasks(task_repo, tasks_data, project_id):
    empty = True
    n = 0
    for task_data in tasks_data:
        task = Task(app_id=project_id)
        [setattr(task, k, v) for k, v in task_data.iteritems()]
        found = task_repo.get_task_by(app_id=project_id, info=task.info)
        if found is None:
            task_repo.save(task)
            n += 1
            empty = False
    if empty:
        msg = gettext('It looks like there were no new records to import')
        return msg
    msg = str(n) + " " + gettext('new tasks were imported successfully')
    if n == 1:
        msg = str(n) + " " + gettext('new task was imported successfully')
    cached_apps.delete_n_tasks(project_id)
    cached_apps.delete_n_task_runs(project_id)
    cached_apps.delete_overall_progress(project_id)
    cached_apps.delete_last_activity(project_id)
    return msg


_importers = {'csv': _BulkTaskCSVImport,
              'gdocs': _BulkTaskGDImport,
              'epicollect': _BulkTaskEpiCollectPlusImport}
