# -*- coding: utf8 -*-
# This file is part of PYBOSSA.
#
# Copyright (C) 2015 Scifabric LTD.
#
# PYBOSSA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PYBOSSA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PYBOSSA.  If not, see <http://www.gnu.org/licenses/>.
"""
PYBOSSA api module for exposing domain object TaskRun via an API.

This package adds GET, POST, PUT and DELETE methods for:
    * task_runs

"""
import json
import time
from flask import request, Response, current_app
from flask_login import current_user
from pybossa.model.review import Review
from werkzeug.exceptions import Forbidden, BadRequest

from .api_base import APIBase
from pybossa.util import get_user_id_or_ip, get_avatar_url
from pybossa.core import task_repo, sentinel, anonymizer, project_repo
from pybossa.core import uploader
from pybossa.contributions_guard import ContributionsGuard
from pybossa.auth import jwt_authorize_project
from pybossa.auth import ensure_authorized_to, is_authorized
from pybossa.sched import can_post


class ReviewAPI(APIBase):

    """Class API for domain object TaskRun."""

    __class__ = Review
    reserved_keys = set(['id', 'created', 'finish_time'])

    def check_can_post(self, project_id, task_id, user_ip_or_id):
        if not can_post(project_id, task_id, user_ip_or_id):
            raise Forbidden("You must request a task first!")

    def _update_object(self, review):
        """Update task_run object with user id or ip."""
        #self.check_can_post(taskrun.project_id, taskrun.task_id, get_user_id_or_ip())
        #task = task_repo.get_task(taskrun.task_id)
        #guard = ContributionsGuard(sentinel.master)

        #self._validate_project_and_task(taskrun, task)
        #self._ensure_task_was_requested(task, guard)
        #self._add_user_info(review)
        #self._add_created_timestamp(taskrun, task, guard)
        review.user_id = current_user.id


