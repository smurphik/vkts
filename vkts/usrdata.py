#! /usr/bin/env python3

"""Module for working with data stored in the directory .vkts/.
These include user accounts, emails, communities and universities
of interest to user, topics, etc."""

import os
import json
from .utils import exception_handler


class UsrData:

    # paths to data files
    data_path = '.vkts'
    acc_path = os.sep.join((data_path, 'accounts.json'))
    adm_path = os.sep.join((data_path, 'adm_data.json'))
    univ_path = os.sep.join((data_path, 'univers.json'))
    # data type file name -> file path
    path_map = {'acc': acc_path,
                'adm': adm_path,
                'univ': univ_path}

    def generate_if_absent(self):
        """Generate user data blank if absent"""

        if not os.path.isdir(self.data_path):
            os.mkdir(self.data_path)
        if not os.path.isfile(self.acc_path):
            #acc_obj = {"email": None, "vk": None, "telegram": None}
            json.dump({}, open(self.acc_path, 'w'))
        if not os.path.isfile(self.adm_path):
            adm_obj = {"bc_emails": [], "mon_groups": []}
            json.dump(adm_obj, open(self.adm_path, 'w'))
        if not os.path.isfile(self.univ_path):
            json.dump({}, open(self.univ_path, 'w'))

    def open(self):
        """Open user data"""

        try:
            self.acc = json.load(open(self.acc_path))
            self.adm = json.load(open(self.adm_path))
            self.univ = json.load(open(self.univ_path))
        except Exception as e:
            exception_handler(e, 'Incorrect data in ' + self.data_path)

    def get(self, *field_path):
        """Safe get object of UsrData. For instance:

         >>> u = UsrData()
         >>> is_act = u.get('acc', 'vk', 'charm', 'is_activated')

        to know, is account `charm` activated"""

        self.open()

        try:
            # go down the data structure untill target (or None if absent)
            d = self.__dict__
            fields = list(field_path)
            for f in fields:
                if d is None:
                    return None
                if isinstance(f, int):
                    assert(isinstance(d, list))
                    if f < len(d):
                        d = d[f]
                    else:
                        return None
                else:
                    if f in d:
                        d = d[f]
                    else:
                        return None
            return d

        except Exception as e:
            exception_handler(e, 'Reading user data error')

    def set(self, new_obj, *field_path, correct_is_act=False):
        """Safe write to UsrData instance with data file update.
        For instance do:

          >>> u = UsrData()
          >>> u.set(True, 'acc', 'vk', 'charm', 'is_activated')

        to write `True` into u.acc['vk']['charm']['is_activated']"""

        self.generate_if_absent()
        self.open()

        try:
            # look for/create the specified place in the object
            d = self.__dict__
            fields = list(field_path)
            last = fields.pop()
            for f in fields:
                if f not in d or d[f] is None:
                    d[f] = {}
                d = d[f]

            # update user data in memory
            if last in d and isinstance(d[last], list):
                d[last].append(new_obj)
            else:
                d.update(((last, new_obj),))

            # Correct attribut `is_activated`
            # (activate random if there is a single object)
            if correct_is_act and len(d) > 0:
                attr_list = [x['is_activated'] for x in d.values()]
                if not list(filter(bool, attr_list)):
                    name = list(d.keys())[0]
                    d[name]['is_activated'] = True

            # update user data in data file
            data_type = field_path[0]
            file_path = self.path_map[data_type]
            json.dump(self.__dict__[data_type], open(file_path, 'w'))

        except Exception as e:
            exception_handler(e, 'Saving user data error')

    def del_(self, *field_path, correct_is_act=False):
        """Safe delete object from UsrData with data file update.
        For instance:

         >>> u = UsrData()
         >>> u.del_('acc', 'vk', 'charm')

        to delete `charm`"""

        self.generate_if_absent()
        self.open()

        try:
            # go down the data structure untill target (or None if absent)
            d = self.__dict__
            fields = list(field_path)
            last = fields.pop()
            for f in fields:
                if d is None:
                    return None
                if isinstance(f, int):
                    assert(isinstance(d, list))
                    if f < len(d):
                        d = d[f]
                    else:
                        return None
                else:
                    if f in d:
                        d = d[f]
                    else:
                        return None

            # del
            if isinstance(d, list):
                if isinstance(last, int):
                    if last < len(d):
                        #print('list[int]: {}, {}'.format(d, last))
                        del d[last]
                else:
                    if last in d:
                        #print('list.remove(str): {}, {}'.format(d, last))
                        d.remove(last)
            elif isinstance(d, dict):
                if last in d:
                    #print('dict[str]: {}, {}'.format(d, last))
                    del d[last]

            # Correct attribut `is_activated`
            # (activate random if there is a single object)
            if correct_is_act and len(d) > 0:
                attr_list = [x['is_activated'] for x in d.values()]
                if not list(filter(bool, attr_list)):
                    name = list(d.keys())[0]
                    d[name]['is_activated'] = True

            # update user data in data file
            data_type = field_path[0]
            file_path = self.path_map[data_type]
            json.dump(self.__dict__[data_type], open(file_path, 'w'))

        except Exception as e:
            exception_handler(e, 'Deleting user data error')

    def drop_activations(self, *field_path):
        """Set `False` to all objects in objects dictionary"""

        self.generate_if_absent()
        self.open()

        # get objects dictionary
        objs_dict = self.get(*field_path)

        try:
            # drop attribute
            for obj_key in objs_dict.keys():
                objs_dict[obj_key]['is_activated'] = False

            # update user data in data file
            data_type = field_path[0]
            file_path = self.path_map[data_type]
            json.dump(self.__dict__[data_type], open(file_path, 'w'))

        except Exception as e:
            exception_handler(e, 'Droping attribute error in user data')

    def get_active_obj(self, *field_path):
        """Find activated objects on end of field path.
        Returns: object_name, object"""

        self.open()

        # get objects dictionary
        objs_dict = self.get(*field_path)

        try:
            # find activated object
            for obj_key in objs_dict.keys():
                if objs_dict[obj_key]['is_activated']:
                    break
            else:
                raise

            return obj_key, objs_dict[obj_key]

        except Exception as e:
            exception_handler(e, '\n'.join(
                'Active {} account is not found.',
                '(Maybe need to execute command ac_add for',
                'adding account of type \'vk\' is needed or',
                'other *_add command)'))
