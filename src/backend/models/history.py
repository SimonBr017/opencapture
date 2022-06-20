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

# @dev : Nathan Cheval <nathan.cheval@outlook.fr>

from src.backend.main import create_classes_from_current_config


def add_history(args):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    args = {
        'table': 'history',
        'columns': {
            'history_submodule': args['submodule'],
            'history_module': args['module'],
            'user_info': args['user_info'],
            'history_desc': args['desc'],
            'user_id': args['user_id'],
            'user_ip': args['ip'],
        }
    }
    _db.insert(args)
    return True, ''


def get_history(args):
    _vars = create_classes_from_current_config()
    _db = _vars[0]
    error = None
    _history = _db.select({
        'select': ['*'] if 'select' not in args else args['select'],
        'table': ['history'],
        'where': args['where'] if 'where' in args else [],
        'data': args['data'] if 'data' in args else [],
        'order_by': args['order_by'] if 'limit' in args else [],
        'limit': str(args['limit']) if 'limit' in args else [],
        'offset': str(args['offset']) if 'offset' in args else [],
    })
    return _history, error
