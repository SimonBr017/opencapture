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

# @dev : Nathan Cheval <nathan.cheval@edissyum.com>

import os
import json
from flask_cors import CORS
from flask_babel import Babel
from flask import request, session, Flask



app = Flask(__name__, instance_relative_config=True)
babel = Babel(app)
CORS(app, supports_credentials=True)

app.config.from_mapping(
    SECRET_KEY='941fbd79ac86cfe33b0c8cd5ff497341',
    CONFIG_FILE=os.path.join(app.instance_path, 'config.ini'),
    CONFIG_FOLDER=os.path.join(app.instance_path, 'config/'),
    LANG_FILE=os.path.join(app.instance_path, 'lang.json'),
    UPLOAD_FOLDER=os.path.join(app.instance_path, 'upload/verifier/'),
    UPLOAD_FOLDER_SPLITTER=os.path.join(app.instance_path, 'upload/splitter/'),
    BABEL_TRANSLATION_DIRECTORIES=app.root_path.replace('backend', 'assets') + '/i18n/backend/translations/'
)

langs = json.loads(open(app.config['LANG_FILE']).read())
app.config['LANGUAGES'] = langs


@babel.localeselector
def get_locale():
    if 'lang' not in session:
        session['lang'] = request.accept_languages.best_match(app.config['LANGUAGES'].keys())

    return session['lang']


if __name__ == "__main__":
    app.run()
