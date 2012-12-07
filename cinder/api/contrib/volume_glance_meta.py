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

from cinder.api import extensions
from cinder.api.openstack import wsgi


FLAGS = flags.FLAGS

class VolumeGlanceMetadataController(wsgi.Controller):
    def __init__(self, *args, **kwargs):
        super(VolumeGlanceMetadataController, self).__init__(*args, **kwargs)
        self.volume_api = volume.API()


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