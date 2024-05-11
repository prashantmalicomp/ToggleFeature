# validate env function
from app.models import FeatureToggle, EnvironmentEnum


def validate_env(env, toggle_id=None, user=None):
    """
    :param env: Query params of selected ENV
    :param toggle_id: toggle featuer id
    :param user: login user id
    :return: Boolean
    """
    user_id = user.id

    if env not in [env.name for env in EnvironmentEnum]:
        return "please enter valid env like ['DEV', 'QA', 'PROD', 'PERFQA', 'UAT]"

    if toggle_id:
        toggle = FeatureToggle.query.filter(
            FeatureToggle.sb_id == toggle_id,
            FeatureToggle.status == 'ACTIVE'
        ).first()

        if toggle:
            if str(toggle.environment) != str(env):
                return f"Update Failed : Please select valid ENV of respective toggle_id={toggle_id} Valid ENV - {toggle.environment}"
            if toggle.created_by != user_id:
                return f"Update Failed : Toggle not created by login user = {user_id}"

        if user.role == 'ADMIN':
            return False

    return False


