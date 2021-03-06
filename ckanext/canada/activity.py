from ckantoolkit import h
from ckan.logic import get_action
from ckan.common import _, ungettext
from ckan.lib.helpers import url_for
import datetime

MERGE_ACTIVITIES_WITHIN_SECONDS = 2


def datastore_activity_create(context, act_data):
    activity_type = act_data['activity_type']
    count = act_data['count']
    resource_id = act_data['resource_id']
    user = context['user']
    model = context['model']
    user_id = model.User.by_name(user.decode('utf8')).id
    if activity_type == 'deleted datastore':
        #  get last deleted activity for this user, if within 2 seconds,
        #   merge these activities
        act = model.activity.user_activity_list(user_id, 1, 0)
        now = datetime.datetime.now()
        if act and len(act)>0 and (
                now - act[0].timestamp).total_seconds()<MERGE_ACTIVITIES_WITHIN_SECONDS and (
                act[0].activity_type == activity_type):
            act = act[0]
            act.data['count'] += count
            #avoid version
            model.Session.query(model.Activity).filter_by(id=act.id).update(
                {"data": act.data})
            model.Session.refresh(act)
            model.Session.flush()
            model.repo.commit()
            return
    res_obj = model.Resource.get(resource_id)
    pkg = model.Package.get(res_obj.package_id)
    org = model.Group.get(pkg.owner_org)
    activity_dict = {
        'user_id': user_id,
        'object_id': res_obj.package_id,
        'activity_type': activity_type,
    }
    activity_dict['data'] = {
        'resource_id': resource_id,
        'pkg_type': pkg.type,
        'resource_name': res_obj.name,
        'owner_org': org.name,
        'count': count,
    }
    activity_create_context = {
        'model': context['model'],
        'user': context['user'],
        'defer_commit': False,
        'ignore_auth': True,
        'session': context['session'],
    }
    get_action('activity_create')(activity_create_context, activity_dict)
