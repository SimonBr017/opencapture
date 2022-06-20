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
from src.backend.import_rest import auth, locale, config, user, splitter, verifier, roles, privileges, custom_fields, \
    forms, status, accounts, outputs, maarch, inputs, positions_masks, history, doctypes


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

app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)
app.register_blueprint(roles.bp)
app.register_blueprint(forms.bp)
app.register_blueprint(inputs.bp)
app.register_blueprint(locale.bp)
app.register_blueprint(status.bp)
app.register_blueprint(config.bp)
app.register_blueprint(maarch.bp)
app.register_blueprint(outputs.bp)
app.register_blueprint(history.bp)
app.register_blueprint(splitter.bp)
app.register_blueprint(accounts.bp)
app.register_blueprint(verifier.bp)
app.register_blueprint(privileges.bp)
app.register_blueprint(custom_fields.bp)
app.register_blueprint(positions_masks.bp)
app.register_blueprint(doctypes.bp)


@babel.localeselector
def get_locale():
    if 'lang' not in session:
        session['lang'] = request.accept_languages.best_match(app.config['LANGUAGES'].keys())

    return session['lang']


if __name__ == "__main__":
    app.run()
