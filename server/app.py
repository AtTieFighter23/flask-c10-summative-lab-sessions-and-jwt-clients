from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, Note
from schemas import user_schema, note_schema, notes_schema


# ---------- Auth Resources ----------

class Signup(Resource):
    def post(self):
        data = request.get_json()
        errors = []

        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        password_confirmation = data.get('password_confirmation') or ''

        if not username:
            errors.append('Username is required.')
        elif User.query.filter_by(username=username).first():
            errors.append('Username is already taken.')

        if not password:
            errors.append('Password is required.')
        elif password != password_confirmation:
            errors.append('Password and confirmation do not match.')

        if errors:
            return {'errors': errors}, 422

        user = User(username=username)
        user.password_hash = password
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        return user_schema.dump(user), 201


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username') or ''
        password = data.get('password') or ''

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user_schema.dump(user), 200

        return {'errors': ['Invalid username or password.']}, 401


class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                return user_schema.dump(user), 200
        return {'error': 'Not logged in.'}, 401


# ---------- Note Resources ----------

class NoteIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized.'}, 401

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = Note.query.filter_by(user_id=user_id).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            'notes': notes_schema.dump(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
        }, 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized.'}, 401

        data = request.get_json()
        errors = []
        title = (data.get('title') or '').strip()
        content = (data.get('content') or '').strip()

        if not title:
            errors.append('Title is required.')
        if not content:
            errors.append('Content is required.')

        if errors:
            return {'errors': errors}, 422

        note = Note(title=title, content=content, user_id=user_id)
        db.session.add(note)
        db.session.commit()

        return note_schema.dump(note), 201


class NoteByID(Resource):
    def _get_owned_note(self, id, user_id):
        return Note.query.filter_by(id=id, user_id=user_id).first()

    def get(self, id):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized.'}, 401

        note = self._get_owned_note(id, user_id)
        if not note:
            return {'error': 'Note not found.'}, 404

        return note_schema.dump(note), 200

    def patch(self, id):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized.'}, 401

        note = self._get_owned_note(id, user_id)
        if not note:
            return {'error': 'Note not found.'}, 404

        data = request.get_json()
        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = data['content']

        db.session.commit()
        return note_schema.dump(note), 200

    def delete(self, id):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized.'}, 401

        note = self._get_owned_note(id, user_id)
        if not note:
            return {'error': 'Note not found.'}, 404

        db.session.delete(note)
        db.session.commit()
        return {}, 204


api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(NoteIndex, '/notes')
api.add_resource(NoteByID, '/notes/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)