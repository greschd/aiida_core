# -*- coding: utf-8 -*-
from aiida.common.exceptions import ValidationError, ParsingError

__copyright__ = u"Copyright (c), 2014, École Polytechnique Fédérale de Lausanne (EPFL), Switzerland, Laboratory of Theory and Simulation of Materials (THEOS). All rights reserved."
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file"
__version__ = "0.2.1"

class OutputParsingError(ParsingError):
    pass

class FailedJobError(ValidationError):
    pass        
