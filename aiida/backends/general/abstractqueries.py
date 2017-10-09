# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
from abc import ABCMeta, abstractmethod


class AbstractQueryManager(object):
    __metaclass__ = ABCMeta


    def __init__(self,  *args, **kwargs):
        pass


    # This is an example of a query that could be overriden by a better implementation,
    # for performance reasons:
    def query_jobcalculations_by_computer_user_state(
            self, state, computer=None, user=None,
            only_computer_user_pairs=False,
            only_enabled=True, limit=None
    ):
        """
        Filter all calculations with a given state.

        Issue a warning if the state is not in the list of valid states.

        :param string state: The state to be used to filter (should be a string among
                those defined in aiida.common.datastructures.calc_states)
        :param computer: a Django DbComputer entry, or a Computer object, of a
                computer in the DbComputer table.
                A string for the hostname is also valid.
        :param user: a Django entry (or its pk) of a user in the DbUser table;
                if present, the results are restricted to calculations of that
                specific user
        :param bool only_computer_user_pairs: if False (default) return a queryset
                where each element is a suitable instance of Node (it should
                be an instance of Calculation, if everything goes right!)
                If True, return only a list of tuples, where each tuple is
                in the format
                ('dbcomputer__id', 'user__id')
                [where the IDs are the IDs of the respective tables]
        :param int limit: Limit the number of rows returned

        :return: a list of calculation objects matching the filters.
        """
        # I assume that calc_states are strings. If this changes in the future,
        # update the filter below from dbattributes__tval to the correct field.
        from aiida.orm.computer import Computer
        from aiida.orm.calculation.job import JobCalculation
        from aiida.orm.user import User
        from aiida.orm.querybuilder import QueryBuilder
        from aiida.common.exceptions import InputValidationError
        from aiida.common.datastructures import calc_states

        if state not in calc_states:
            raise InputValidationError("querying for calculation state='{}', but it "
                                "is not a valid calculation state".format(state))

        calcfilter = {'state': {'==': state}}
        computerfilter = {"enabled": {'==': True}}
        userfilter = {}

        if computer is None:
            pass
        elif isinstance(computer, int):
            computerfilter.update({'id': {'==': computer}})
        elif isinstance(computer, Computer):
            computerfilter.update({'id': {'==': computer.pk}})
        else:
            try:
                computerfilter.update({'id': {'==': computer.id}})
            except AttributeError as e:
                raise Exception(
                    "{} is not a valid computer\n{}".format(computer, e)
                )
        if user is None:
            pass
        elif isinstance(user, int):
            userfilter.update({'id': {'==': user}})
        else:
            try:
                userfilter.update({'id': {'==': int(user.id)}})
                # Is that safe?
            except:
                raise Exception("{} is not a valid user".format(user))

        qb = QueryBuilder()
        qb.append(type="computer", tag='computer', filters=computerfilter)
        qb.append(JobCalculation, filters=calcfilter, tag='calc', has_computer='computer')
        qb.append(type="user", tag='user', filters=userfilter,
                  creator_of="calc")

        if only_computer_user_pairs:
            qb.add_projection("computer", "*")
            qb.add_projection("user", "*")
            returnresult = qb.distinct().all()
        else:
            qb.add_projection("calc", "*")
            if limit is not None:
                qb.limit(limit)
            returnresult = qb.all()
            returnresult = zip(*returnresult)[0]
        return returnresult


    def get_creation_statistics(
            self,
            user_email=None
    ):
        """
        Return a dictionary with the statistics of node creation, summarized by day.

        :note: Days when no nodes were created are not present in the returned `ctime_by_day` dictionary.

        :param user_email: If None (default), return statistics for all users.
            If an email is specified, return only the statistics for the given user.

        :return: a dictionary as
            follows::

                {
                   "total": TOTAL_NUM_OF_NODES,
                   "types": {TYPESTRING1: count, TYPESTRING2: count, ...},
                   "ctime_by_day": {'YYYY-MMM-DD': count, ...}

            where in `ctime_by_day` the key is a string in the format 'YYYY-MM-DD' and the value is
            an integer with the number of nodes created that day.
        """
        from aiida.orm.querybuilder import QueryBuilder as QB
        from aiida.orm import User, Node
        from collections import Counter
        import datetime

        def count_statistics(dataset):

            def get_statistics_dict(dataset):
                results = {}
                for count, typestring in sorted(
                        (v, k) for k, v in dataset.iteritems())[::-1]:
                    results[typestring] = count
                return results

            count_dict = {}

            types = Counter([r[2] for r in dataset])
            count_dict["types"] = get_statistics_dict(types)

            ctimelist = [r[1].strftime("%Y-%m-%d") for r in dataset]
            ctime = Counter(ctimelist)

            if len(ctimelist) > 0:

                # For the way the string is formatted, we can just sort it alphabetically
                firstdate = datetime.datetime.strptime(sorted(ctimelist)[0], '%Y-%m-%d')
                lastdate = datetime.datetime.strptime(sorted(ctimelist)[-1], '%Y-%m-%d')

                curdate = firstdate
                outdata = {}

                while curdate <= lastdate:
                    curdatestring = curdate.strftime('%Y-%m-%d')
                    outdata[curdatestring] = ctime.get(curdatestring, 0)
                    curdate += datetime.timedelta(days=1)
                count_dict["ctime_by_day"] = outdata

            else:
                count_dict["ctime_by_day"] = {}

            return count_dict

        statistics = {}

        q = QB()
        q.append(Node, project=['id', 'ctime', 'type'], tag='node')
        if user_email is not None:
            q.append(User, creator_of='node', project='email', filters={'email': user_email})
        qb_res = q.all()

        # total count
        statistics["total"] = len(qb_res)
        statistics.update(count_statistics(qb_res))

        return statistics

