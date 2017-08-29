# coding:utf-8

from __future__ import absolute_import, unicode_literals
from ctypes import string_at
import fnmatch
import json
import re
import unicodedata
import base64
import time
from IPy import IP
from sqlalchemy import event, Numeric, BigInteger, or_
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float, Text, Table, func, \
    Binary as BinaryType, and_, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, relation
from sqlalchemy.orm.exc import NoResultFound
from database.exceptions import ApplicationError
from database.helpers import before_save, before_insert, before_update, lower_and_encode

Base = declarative_base()