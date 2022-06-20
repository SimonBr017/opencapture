# This file is part of Open-Capture for Invoices.

# Open-Capture for Invoices is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Open-Capture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Open-Capture for Invoices. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.

# @dev : Oussama Brich <oussama.brich@edissyum.com>

from gettext import gettext
from src.backend.main import create_classes_from_current_config


def add_doctype(args):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    doctypes, error = retrieve_doctypes({
        'where': ['key = %s', 'form_id = %s', 'status <> %s'],
        'data': [args['key'], args['form_id'], 'DEL']
    })

    if not doctypes:
        args = {
            'table': 'doctypes',
            'columns': {
                'type': args['type'],
                'key': args['key'],
                'label': args['label'],
                'code': args['code'],
                'form_id': args['form_id'],
                'is_default': args['is_default'],
            }
        }
        res = _db.insert(args)

        if not res:
            error = gettext('ADD_DOCTYPE_ERROR')
        return res, error
    else:
        error = gettext('DOCTYPE_ALREADY_EXIST')

    return '', error


def retrieve_doctypes(args):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    error = None
    doctypes = _db.select({
        'select': ['*'] if 'select' not in args else args['select'],
        'table': ['doctypes'],
        'where': ['status<>%s'] if 'where' not in args else args['where'],
        'data': ['DEL'] if 'data' not in args else args['data'],
        'order_by': ["id ASC"],
    })

    return doctypes, error


def update(args):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    error = None
    res = _db.update({
        'table': ['doctypes'],
        'set': {
            'label': args['label'],
            'code': args['code'],
            'status': args['status'],
            'is_default': args['is_default'],
        },
        'where': ['status <> %s', 'key = %s', 'form_id = %s'],
        'data': ['DEL', args['key'], args['form_id']]
    })

    if not res:
        error = gettext('UPDATE_DOCTYPE_ERROR')

    return res, error


def set_default(args):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    error = None
    res = _db.update({
        'table': ['doctypes'],
        'set': {
            'is_default': False
        },
        'where': ['status <> %s', 'form_id = %s'],
        'data': ['DEL', args['form_id']]
    })
    if res:
        res = _db.update({
            'table': ['doctypes'],
            'set': {
                'is_default': True
            },
            'where': ['status <> %s', 'key = %s', 'form_id = %s'],
            'data': ['DEL', args['key'], args['form_id']]
        })
        if not res:
            error = gettext('SET_DEFAULT_DOCTYPE_ERROR')
            return '', error
    else:
        error = gettext('SET_DEFAULT_DOCTYPE_ERROR')
    return res, error
