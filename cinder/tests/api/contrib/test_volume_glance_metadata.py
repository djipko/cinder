# vim: tabstop=4 shiftwidth=4 softtabstop=4

#   Copyright 2012 OpenStack LLC.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import datetime
import json
import uuid

from lxml import etree
import webob

from cinder import context
from cinder import test
from cinder import volume
from cinder.tests.api.openstack import fakes


def fake_volume_get(*args, **kwargs):
    return {
        'id': 'fake',
        'host': 'host001',
        'status': 'available',
        'size': 5,
        'availability_zone': 'somewhere',
        'created_at': datetime.datetime.now(),
        'attach_status': None,
        'display_name': 'anothervolume',
        'display_description': 'Just another volume!',
        'volume_type_id': None,
        'snapshot_id': None,
        'project_id': 'fake',
    }


def fake_volume_get_all(*args, **kwargs):
    return [fake_volume_get()]


fake_glance_metadata = {
    u'image_id': u'someid',
    u'image_name': u'fake',
    u'kernel_id': u'somekernel',
    u'ramdisk_id': u'someramdisk',
}


def fake_get_volume_glance_metadata(*args, **kwargs):
    return fake_glance_metadata


def app():
    # no auth, just let environ['cinder.context'] pass through
    api = fakes.router.APIRouter()
    mapper = fakes.urlmap.URLMap()
    mapper['/v1'] = api
    return mapper


class VolumeGlanceMetadata(test.TestCase):
    
    def setUp(self):
        super(VolumeGlanceMetadata, self).setUp()
        self.stubs.Set(volume.API, 'get', fake_volume_get)
        self.stubs.Set(volume.API, 'get_all', fake_volume_get_all)
        self.stubs.Set(volume.API, 'get_volume_glance_metadata',
                       fake_get_volume_glance_metadata)
        self.UUID = uuid.uuid4()

    def test_get_volume_allowed(self):
        ctx = context.RequestContext('admin', 'fake', True)
        req = webob.Request.blank('/v1/fake/volumes/%s' % self.UUID)
        req.method = 'GET'
        req.environ['cinder.context'] = ctx
        res = req.get_response(app())
        vol = json.loads(res.body)['volume']
        self.assertTrue('volume_glance_metadata' in vol)
        self.assertEqual(vol['volume_glance_metadata'], fake_glance_metadata)

    def test_get_volume_unallowed(self):
        ctx = context.RequestContext('non-admin', 'fake', False)
        req = webob.Request.blank('/v1/fake/volumes/%s' % self.UUID)
        req.method = 'GET'
        req.environ['cinder.context'] = ctx
        res = req.get_response(app())
        vol = json.loads(res.body)['volume']
        self.assertFalse('volume_glance_metadata' in vol)

    def test_list_detail_volumes_allowed(self):
        ctx = context.RequestContext('admin', 'fake', True)
        req = webob.Request.blank('/v1/fake/volumes/detail')
        req.method = 'GET'
        req.environ['cinder.context'] = ctx
        res = req.get_response(app())
        vol = json.loads(res.body)['volumes']
        self.assertTrue('volume_glance_metadata' in vol[0])
        self.assertEqual(vol[0]['volume_glance_metadata'], fake_glance_metadata)

    def test_list_detail_volumes_unallowed(self):
        ctx = context.RequestContext('non-admin', 'fake', False)
        req = webob.Request.blank('/v1/fake/volumes/detail')
        req.method = 'GET'
        req.environ['cinder.context'] = ctx
        res = req.get_response(app())
        vol = json.loads(res.body)['volumes']
        self.assertFalse('volume_glance_metadata' in vol[0])

    def test_get_volume_xml(self):
        ctx = context.RequestContext('admin', 'fake', True)
        req = webob.Request.blank('/v1/fake/volumes/%s' % self.UUID)
        req.method = 'GET'
        req.accept = 'application/xml'
        req.environ['cinder.context'] = ctx
        res = req.get_response(app())
        vol = etree.XML(res.body)
        vol.get('volume_glance_metadata')

    def test_list_volumes_detail_xml(self):
        ctx = context.RequestContext('admin', 'fake', True)
        req = webob.Request.blank('/v1/fake/volumes/detail')
        req.method = 'GET'
        req.accept = 'application/xml'
        req.environ['cinder.context'] = ctx
        res = req.get_response(app())
        vol = list(etree.XML(res.body))[0]
        vol.get('volume_glance_metadata')
