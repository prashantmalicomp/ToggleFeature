from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.models import db, FeatureToggle, User
from app.toggles.serde import FeatureToggleSchema
from app.helper.validator import validate_env

toggle_blueprint = Blueprint('toggle_blueprint', __name__, url_prefix='/api/v1')


@toggle_blueprint.route('/toggles', methods=['GET'])
def get_toggles():
    toggles = FeatureToggle.query.all()
    return FeatureToggleSchema(many=True).jsonify(toggles), 200


@toggle_blueprint.route('/toggles/<int:toggle_id>', methods=['GET'])
def get_toggle(toggle_id):
    params = request.args

    version = params.get('version')
    status = params.get('status')

    toggle = FeatureToggle.query.filter(
        FeatureToggle.sb_id == toggle_id
    )

    if not toggle:
        return {'error': 'Toggle not found'}

    # toggle filter by version
    if version:
        toggle = toggle.filter(FeatureToggle.version == version)

    # toggle filter by status
    if status:
        toggle = toggle.filter(FeatureToggle.status == status)

    return FeatureToggleSchema(many=True).jsonify(toggle), 200


# Define API endpoints within the Blueprint
@toggle_blueprint.route('/toggles/<string:env>/<int:user_id>', methods=['POST'])
def create_toggle(env, user_id):
    """
    :param env: Env for creating toggle
    :param user_id: user id
    :return:
    """
    toggle_env = env

    data = request.json

    if not user_id or not toggle_env:
        return jsonify({'error': 'Please select ENV - "env" & Toggle User ID - "user_id" '}), 404

    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    identifier = data.get('identifier')

    toggle = FeatureToggle.query.filter(func.lower(FeatureToggle.identifier) == str(identifier).lower()).first()

    if toggle:
        return jsonify({'error': f'Toggle - {identifier} already exists'}), 404

    verify_env = validate_env(toggle_env, None, user)
    if verify_env:
        return jsonify({'error': verify_env}), 400

    try:
        data = FeatureToggleSchema().load(data)

        # configure env data
        data['environment'] = env
        data['updated_by'] = user_id
        data['created_by'] = user_id
        data['status'] = 'ACTIVE'

        toggle = FeatureToggle(**data)

        db.session.add(toggle)
        db.session.flush()
        toggle.sb_id = toggle.id
        db.session.commit()
        return FeatureToggleSchema().jsonify(toggle), 201

    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
    except IntegrityError as err:
        return jsonify({'error': str(err.orig)})
    except Exception as err:
        return jsonify({'error': str(err)})


@toggle_blueprint.route('/toggles/<int:toggle_id>', methods=['PUT'])
def update_toggle(toggle_id):
    params = request.args
    toggle_env = params.get('env')
    user_id = params.get('user_id')

    data = request.json

    # validate ENV for updating toggle
    if not user_id or not toggle_env:
        return jsonify({'error': 'Please select ENV - "env" & Toggle User ID - "user_id" '}), 404

    user = User.query.get(user_id)

    # check login user is exists
    if not User.query.get(user_id):
        return jsonify({'error': 'User not found'}), 404

    # check update toggle exists or not
    toggle = FeatureToggle.query.filter(
        FeatureToggle.sb_id == toggle_id,
        FeatureToggle.status == 'ACTIVE'
    ).first()

    if not toggle:
        return jsonify({'error': 'Toggle not found'}), 404

    # Verify updating toggle by correct login user & role if user role is admin then update for all toggles
    verify_env = validate_env(toggle_env, toggle_id, user)
    if verify_env:
        return jsonify({'error': verify_env}), 400

    try:
        data = FeatureToggleSchema().load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    try:

        # create new clone copy of given update toggle id for maintaining version
        new_clone = toggle.clone_model()

        # update active toggle as SUPERSEDED because new toggle version is active
        toggle.status = 'SUPERSEDED'
        toggle.updated_by = user_id
        data['updated_by'] = user_id

        for field in ['identifier', 'description', 'state', 'notes', 'updated_by']:
            setattr(new_clone, field, data.get(field, getattr(toggle, field)))

        # fetch current versio 
        current_version = toggle.version

        # set new version
        new_clone.version = current_version + 1
        new_clone.sb_id = toggle.sb_id
        new_clone.status = 'ACTIVE'
        db.session.add(toggle)
        db.session.commit()


    except IntegrityError as err:
        return jsonify({'error': str(err.orig)}), 404
    except Exception as err:
        return jsonify({'error': str(err)}),

    return FeatureToggleSchema().jsonify(new_clone)
