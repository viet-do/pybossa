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

from sqlalchemy import Integer, Text
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from pybossa.core import db
from pybossa.model import DomainObject, make_timestamp



class Review(db.Model, DomainObject):
    '''A run of a given task by a specific user.
    '''
    __tablename__ = 'review'

    #: ID of the TaskRun
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer)

    #: UTC timestamp for when TaskRun is delivered to user.
    created = Column(Text, default=make_timestamp)
    
    q1 = Column(Integer)
    q2 = Column(Integer)
    q3 = Column(Integer)
    q4 = Column(Integer)
    info = Column(JSONB)

