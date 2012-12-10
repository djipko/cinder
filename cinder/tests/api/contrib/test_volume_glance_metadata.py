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
from xml.dom import minidom

import webob

from cinder.api import common
from cinder.api.openstack.wsgi import MetadataXMLDeserializer
from cinder.api.openstack.wsgi import XMLDeserializer
from cinder import test
from cinder.tests.api import fakes
from cinder import volume


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


class VolumeGlanceMetadataTest(test.TestCase):
    content_type = 'application/json'

    def setUp(self):
        super(VolumeGlanceMetadataTest, self).setUp()
        self.stubs.Set(volume.API, 'get', fake_volume_get)
        self.stubs.Set(volume.API, 'get_all', fake_volume_get_all)
        self.stubs.Set(volume.API, 'get_volume_glance_metadata',
                       fake_get_volume_glance_metadata)
        self.UUID = uuid.uuid4()

    def _make_request(self, url):
        req = webob.Request.blank(url)
        req.accept = self.content_type
        res = req.get_response(fakes.wsgi_app())
        return res

    def _get_glance_metadata(self, body):
        return json.loads(body)['volume']['volume_glance_metadata']

    def _get_glance_metadata_list(self, body):
        return [
            volume['volume_glance_metadata']
            for volume in json.loads(body)['volumes']
        ]

    def test_get_volume(self):
        res = self._make_request('/v2/fake/volumes/%s' % self.UUID)
        self.assertEqual(res.status_int, 200)
        self.assertEqual(self._get_glance_metadata(res.body),
                         fake_glance_metadata)

    def test_list_detail_volumes(self):
        res = self._make_request('/v2/fake/volumes/detail')
        self.assertEqual(res.status_int, 200)
        self.assertEqual(self._get_glance_metadata_list(res.body)[0],
                         fake_glance_metadata)


class GlanceMetadataXMLDeserializer(common.MetadataXMLDeserializer):
    metadata_node_name = "volume_glance_metadata"


class VolumeGlanceMetadataXMLTest(VolumeGlanceMetadataTest):
    content_type = 'application/xml'

    def _get_glance_metadata(self, body):
        deserializer = XMLDeserializer()
        volume = deserializer.find_first_child_named(
            minidom.parseString(body), 'volume')
        glance_metadata = deserializer.find_first_child_named(
            volume, 'volume_glance_metadata')
        return MetadataXMLDeserializer().extract_metadata(glance_metadata)

    def _get_glance_metadata_list(self, body):
        deserializer = XMLDeserializer()
        volumes = deserializer.find_first_child_named(
            minidom.parseString(body), 'volumes')
        volume_list = deserializer.find_children_named(volumes, 'volume')
        glance_metadata_list = [
            deserializer.find_first_child_named(
                volume, 'volume_glance_metadata'
            )
            for volume in volume_list]
        return map(MetadataXMLDeserializer().extract_metadata,
                   glance_metadata_list)
