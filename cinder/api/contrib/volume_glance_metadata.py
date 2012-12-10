#   Copyright 2012 OpenStack, LLC.
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

"""The Volume Glance Metadata API extension."""

from cinder import volume
from cinder.api import extensions
from cinder.api import xmlutil
from cinder.api.openstack import wsgi


authorize = extensions.soft_extension_authorizer('volume',
                                                 'volume_glance_metadata')


class VolumeGlanceMetadataController(wsgi.Controller):
    def __init__(self, *args, **kwargs):
        super(VolumeGlanceMetadataController, self).__init__(*args, **kwargs)
        self.volume_api = volume.API()
        
    def _add_glance_metadata(self, context, resp_volume):
        try:
            glance_meta = self.volume_api.get_volume_glance_metadata(
                context, resp_volume)
        except Exception:
            return
        else:
            if glance_meta:
                resp_volume['volume_glance_metadata'] = dict(
                    glance_meta.iteritems())

    @wsgi.extends
    def show(self, req, resp_obj, id):
        context = req.environ['cinder.context']
        if authorize(context):
            resp_obj.attach(xml=VolumeGlanceMetadataTemplate())
            self._add_glance_metadata(context, resp_obj.obj['volume'])
            
    @wsgi.extends
    def detail(self, req, resp_obj):
        context = req.environ['cinder.context']
        if authorize(context):
            for volume in list(resp_obj.obj['volumes']):
                self._add_glance_metadata(context, volume)


class Volume_glance_metadata(extensions.ExtensionDescriptor):
    """Show glance metadata associated with the volume"""

    name = "VolumeGlanceMetadata"
    alias = "os-vol-glance-meta"
    namespace = ("http://docs.openstack.org/volume/ext/"
                 "volume_glance_metadata/api/v1")
    updated = "2012-12-07T00:00:00+00:00"
    
    def get_controller_extensions(self):
        controller = VolumeGlanceMetadataController()
        extension = extensions.ControllerExtension(self, 'volumes', controller)
        return [extension]


class VolumeGlanceMetadataMetadataTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('volume_glance_metadata',
                                       selector='volume_glance_metadata')
        elem = xmlutil.SubTemplateElement(root, 'meta',
                                          selector=xmlutil.get_items)
        elem.set('key', 0)
        elem.text = 1

        return xmlutil.MasterTemplate(root, 1)


class VolumeGlanceMetadataTemplate(xmlutil.TemplateBuilder):
    def construct(self):
        root = xmlutil.TemplateElement('volume', selector='volume')
        root.append(VolumeGlanceMetadataMetadataTemplate())

        alias = Volume_glance_metadata.alias
        namespace = Volume_glance_metadata.namespace

        return xmlutil.SlaveTemplate(root, 1, nsmap={alias: namespace})
