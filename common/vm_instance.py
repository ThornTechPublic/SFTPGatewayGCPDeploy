# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Creates an Instance VM with common defaults."""
import copy
import re
import common
import default

# Properties for this component
BOOTDISKTYPE = default.BOOTDISK
BOOTDISKSIZE = default.BOOTDISKSIZE
CAN_IP_FWD = default.CAN_IP_FWD
DEVIMAGE = 'devImage'
DISK = default.DISK
DISKTYPE = default.DISKTYPE
DISK_RESOURCES = default.DISK_RESOURCES
ENDPOINT_NAME = default.ENDPOINT_NAME
EXTERNAL_IPS = default.EXTERNAL_IPS
GUEST_ACCELERATORS = default.GUEST_ACCELERATORS
INSTANCE_NAME = default.INSTANCE_NAME
MACHINETYPE = default.MACHINETYPE
METADATA = default.METADATA
NETWORKS = default.NETWORKS
SUBNETWORKS = default.SUBNETWORKS
NO_SCOPE = default.NO_SCOPE
PROJECT = default.PROJECT
PROVIDE_BOOT = default.PROVIDE_BOOT
SERVICE_ACCOUNTS = default.SERVICE_ACCOUNTS
SRCIMAGE = default.SRCIMAGE
TAGS = default.TAGS
ZONE = default.ZONE
AUTODELETE_BOOTDISK = 'bootDiskAutodelete'

# Defaults used for modules that imports this one
DEFAULT_DISKTYPE = 'pd-standard'
DEFAULT_EXTERNAL_IPS = ['EPHEMERAL']
DEFAULT_IP_FWD = False
DEFAULT_MACHINETYPE = 'e2-standard-2'
DEFAULT_NETWORKS = ['default']
DEFAULT_PROVIDE_BOOT = True
DEFAULT_BOOTDISKSIZE = 10
DEFAULT_AUTODELETE_BOOTDISK = True
DEFAULT_DATADISKSIZE = 500
DEFAULT_ZONE = 'us-central1-f'
DEFAULT_PERSISTENT = 'PERSISTENT'
DEFAULT_SERVICE_ACCOUNT = [{
    'email': 'default',
    'scopes': [
        'https://www.googleapis.com/auth/cloud.useraccounts.readonly',
        'https://www.googleapis.com/auth/devstorage.read_only',
        'https://www.googleapis.com/auth/logging.write',
        'https://www.googleapis.com/auth/monitoring.write',
    ]
}]

# Set Metadata Value
ATTACHED_DISKS = 'ATTACHED_DISKS'

# Used for SSD special treatment
SCRATCH = 'SCRATCH'

# Blank image used when sourceImage property is not provided.
BLANK_IMAGE = 'empty10gb'

VALID_IP_RE = re.compile(
    r'((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))'
)


def MakeVMName(context):
  """Generates the VM name."""
  name = context.env['name']
  prop = context.properties
  if INSTANCE_NAME in prop:
    return prop[INSTANCE_NAME]
  return common.AutoName(name, default.INSTANCE)


def GenerateComputeVM(context, create_disks_separately=True):
  """Generates one VM instance resource.

  Args:
    context: Template context dictionary.
    create_disks_separately: When true (default), all new disk resources are
      created as separate resources. This is legacy behaviour from when multiple
      disks creation was not allowed in the disks property.
  Returns:
    dictionary representing instance resource.
  """
  prop = context.properties
  boot_disk_type = prop.setdefault(BOOTDISKTYPE, DEFAULT_DISKTYPE)
  prop[default.DISKTYPE] = boot_disk_type
  can_ip_fwd = prop.setdefault(CAN_IP_FWD, DEFAULT_IP_FWD)
  disks = prop.setdefault(default.DISKS, list())
  local_ssd = prop.setdefault(default.LOCAL_SSD, 0)

  if disks:
    if create_disks_separately:
      # Legacy alternative from when multiple disks on creation were not allowed
      new_disks = prop.setdefault(default.DISK_RESOURCES, list())
      SetDiskProperties(context, disks)
      disks, prop[DISK_RESOURCES] = GenerateDisks(context, disks, new_disks)
    else:
      # All new disks (except local ssd) must provide a sourceImage or existing
      # source. Add blank source image if non provided.
      SetDiskProperties(context, disks, add_blank_src_img=True)

  machine_type = prop.setdefault(MACHINETYPE, DEFAULT_MACHINETYPE)
  metadata = prop.setdefault(METADATA, dict())
  SetMetadataDefaults(metadata)
  vm_name = MakeVMName(context)
  provide_boot = prop.setdefault(PROVIDE_BOOT, DEFAULT_PROVIDE_BOOT)
  tags = prop.setdefault(TAGS, dict([('items', [])]))
  zone = prop.setdefault(ZONE, DEFAULT_ZONE)

  if provide_boot:
    dev_mode = DEVIMAGE in prop and prop[DEVIMAGE]
    src_image = common.MakeC2DImageLink(prop[SRCIMAGE], dev_mode)
    boot_name = common.AutoName(context.env['name'], default.DISK, 'boot')
    disk_size = prop.get(BOOTDISKSIZE, DEFAULT_BOOTDISKSIZE)
    disk_type = common.MakeLocalComputeLink(context, DISKTYPE)
    autodelete = prop.get(AUTODELETE_BOOTDISK, DEFAULT_AUTODELETE_BOOTDISK)
    disks = PrependBootDisk(disks, boot_name, disk_type, disk_size, src_image,
                            autodelete)
  if local_ssd:
    disks = AppendLocalSSDDisks(context, disks, local_ssd)
  machine_type = common.MakeLocalComputeLink(context, default.MACHINETYPE)

  # To be consistent with Dev console and gcloud, service accounts need to be
  #  explicitly disabled
  remove_scopes = prop[NO_SCOPE] if NO_SCOPE in prop else False
  if remove_scopes and SERVICE_ACCOUNTS in prop:
    prop.pop(SERVICE_ACCOUNTS)
  else:  # Make sure there is a default service account
    prop.setdefault(SERVICE_ACCOUNTS, copy.deepcopy(DEFAULT_SERVICE_ACCOUNT))

  resource = []
  resource.insert(
      0, {
          'name': vm_name,
          'type': default.INSTANCE,
          'properties': {
              'zone': zone,
              'machineType': machine_type,
              'canIpForward': can_ip_fwd,
              'disks': disks,
              'networkInterfaces': GetNetworkInterfaces(context),
              'tags': tags,
              'metadata': metadata,
          }
      })

  # Pass through any additional properties to the VM
  if SERVICE_ACCOUNTS in prop:
    resource[0]['properties'].update({SERVICE_ACCOUNTS: prop[SERVICE_ACCOUNTS]})
  if GUEST_ACCELERATORS in prop:
    for accelerators in prop[GUEST_ACCELERATORS]:
      accelerators['acceleratorType'] = common.MakeAcceleratorTypeLink(
          context, accelerators['acceleratorType'])
    resource[0]['properties'].update(
        {GUEST_ACCELERATORS: prop[GUEST_ACCELERATORS]})
    # GPUs cannot be attached to live migratable instances. See:
    # https://cloud.google.com/compute/docs/gpus/#restrictions
    resource[0]['properties'].update(
        {'scheduling': {'onHostMaintenance': 'terminate'}})
  return resource


def GetNetworkInterfaces(context):
  """Extracts the network interfaces to be used in the VM creation."""
  props = context.properties

  networks = props.setdefault(NETWORKS, DEFAULT_NETWORKS)
  subnetworks = props.get(SUBNETWORKS, [])
  external_ips = props.get(EXTERNAL_IPS, DEFAULT_EXTERNAL_IPS)

  network_interfaces = []
  for i in range(len(networks)):
    name = 'Interface %d' % i
    network_interface = {
        'network': common.MakeNetworkComputeLink(context, networks[i]),
        'name': name,
    }

    if subnetworks and i < len(subnetworks) and subnetworks[i]:
      network_interface['subnetwork'] = common.MakeSubnetworkComputeLink(
          context, subnetworks[i])

    ip_value = external_ips[i] if i < len(external_ips) else 'NONE'
    is_static_ip = VALID_IP_RE.match(ip_value) is not None
    if ip_value != 'EPHEMERAL' and ip_value != 'NONE' and not is_static_ip:
      raise common.Error(
          ('External IP value "%s" is invalid. Valid values '
           'are: a valid IP Address, EPHEMERAL or NONE.') % ip_value)

    if ip_value == 'EPHEMERAL' or is_static_ip:
      access_config = {
          'name': '%s %s' % (name, default.EXTERNAL),
          'type': default.ONE_NAT,
      }

      if is_static_ip:
        access_config[default.NAT_IP] = ip_value

      network_interface['accessConfigs'] = [access_config]

    network_interfaces.append(network_interface)

  return network_interfaces


def SetMetadataDefaults(metadata):
  """Set default metadata items."""
  # Disable stackdriver monitoring by default.
  items = metadata.setdefault('items', list())
  if not [True for x in items
          if x.get('key', None) == 'google-monitoring-enable']:
    items.append({'key': 'google-monitoring-enable',
                  'value': '0'})
  if not [True for x in items
          if x.get('key', None) == 'google-logging-enable']:
    items.append({'key': 'google-logging-enable',
                  'value': '0'})


def PrependBootDisk(disk_list, name, disk_type, disk_size, src_image,
                    autodelete):
  """Appends the boot disk."""
  # Request boot disk creation (mark for autodelete)
  boot_disk = [{
      'autoDelete': autodelete,
      'boot': True,
      'deviceName': name,
      'initializeParams': {
          'diskType': disk_type,
          'diskSizeGb': disk_size,
          'sourceImage': src_image
      },
      'type': DEFAULT_PERSISTENT,
  }]
  return boot_disk + disk_list


def AppendLocalSSDDisks(context, disk_list, num_of_local_ssd):
  """Apends local ssds."""
  project = context.env[default.PROJECT]
  prop = context.properties
  zone = prop.setdefault(ZONE, DEFAULT_ZONE)
  local_ssd_disks = []
  for i in range(0, num_of_local_ssd):
    local_ssd_disks.append({
        'deviceName': 'local-ssd-%s' % i,
        'type': SCRATCH,
        'interface': 'SCSI',
        'mode': 'READ_WRITE',
        'autoDelete': True,
        'initializeParams': {'diskType': common.LocalComputeLink(
            project, zone, 'diskTypes', 'local-ssd')}
    })
  return disk_list + local_ssd_disks


def SetDiskProperties(context, disks, add_blank_src_img=False):
  """Set properties on each disk to required format.

  Sets default values, and moves properties passed directly into
  initializeParams where required.

  Args:
    context: Template context dictionary.
    disks: List of disks to set properties on.
    add_blank_src_img: When true, link to blank source image is added for new
    disks where a source image is not specified.
  """

  project = context.env[default.PROJECT]
  zone = context.properties.setdefault(ZONE, DEFAULT_ZONE)

  for disk in disks:
    disk.setdefault(default.AUTO_DELETE, True)
    disk.setdefault('boot', False)
    disk.setdefault(default.TYPE, DEFAULT_PERSISTENT)

    # If disk already exists, no properties to change.
    if default.DISK_SOURCE in disk:
      continue

    else:
      disk_init = disk.setdefault(default.INITIALIZEP, dict())
      if disk[default.TYPE] == SCRATCH:
        disk_init.setdefault(DISKTYPE, 'local-ssd')
      else:
        # In the Instance API reference, size and type are within this property
        if disk_init:
          disk_init.setdefault(default.DISK_SIZE, DEFAULT_DATADISKSIZE)
          disk_init.setdefault(default.DISKTYPE, DEFAULT_DISKTYPE)
        # You can also simply pass the size and type properties directly
        else:
          disk_init[default.DISK_SIZE] = disk.pop(default.DISK_SIZE,
                                                  DEFAULT_DATADISKSIZE)
          disk_init[default.DISKTYPE] = disk.pop(default.DISKTYPE,
                                                 DEFAULT_DISKTYPE)

        # If disk name was given as a direct property, move to initializeParams
        if default.DISK_NAME in disk:
          disk_init[default.DISK_NAME] = disk.pop(default.DISK_NAME)

        # Add link to a blank source image where non-specified
        if add_blank_src_img and default.SRCIMAGE not in disk_init:
          disk_init[default.SRCIMAGE] = common.MakeC2DImageLink(BLANK_IMAGE)

      # Change disk type names into URLs
      disk_init[default.DISKTYPE] = common.LocalComputeLink(
          project, zone, 'diskTypes', disk_init[default.DISKTYPE])


def GenerateDisks(context, disk_list, new_disks):
  """Generates as many disks as passed in the disk_list."""
  prop = context.properties
  zone = prop.setdefault(ZONE, DEFAULT_ZONE)
  sourced_disks = []
  disk_names = []
  for disk in disk_list:
    if default.DISK_SOURCE in disk or disk[default.TYPE] == SCRATCH:
      # These disks do not need to be created as separate resources
      sourced_disks.append(disk)
    else:
      # Extract disk parameters and create as separate resource
      disk_init = disk[default.INITIALIZEP]
      if default.DEVICE_NAME in disk:
        d_name = disk[default.DEVICE_NAME]
      elif default.DISK_NAME in disk_init:
        d_name = disk_init[default.DISK_NAME]
      else:
        raise common.Error('deviceName or diskName is needed for each disk in '
                           'this module implemention of multiple disks per vm.')
      new_disks.append({
          'name': d_name,
          'type': default.DISK,
          'properties': {
              'type': disk_init[default.DISKTYPE],
              'sizeGb': disk_init[default.DISK_SIZE],
              'zone': zone
          }
      })
      disk_names.append(d_name)
      source = common.Ref(d_name)
      sourced_disks.append({
          'deviceName': d_name,
          'autoDelete': disk[default.AUTO_DELETE],
          'boot': False,
          'source': source,
          'type': disk[default.TYPE],
      })
  items = prop[METADATA].setdefault('items', list())
  items.append({'key': ATTACHED_DISKS, 'value': ','.join(disk_names)})
  return sourced_disks, new_disks


def AddServiceEndpointIfNeeded(context):
  """If the endpoint property is present, it will add a service endpoint."""
  prop = context.properties
  if ENDPOINT_NAME not in prop:
    return []
  network = common.MakeNetworkComputeLink(context, prop[default.NETWORKS][0])
  reference = '$(ref.' + MakeVMName(context) + '.name)'
  address = common.MakeFQHN(context, reference)
  name = prop[ENDPOINT_NAME]
  resource = [
      {
          'name': name,
          'type': default.ENDPOINT,
          'properties': {
              'addresses': [
                  {'address': address}
              ],
              'dnsIntegration': {
                  'networks': [network]
              }
          }
      }
  ]
  return resource


def GenerateResourceList(context, **kwargs):
  """Returns list of resources generated by this module."""
  resources = GenerateComputeVM(context, **kwargs)
  resources += common.AddDiskResourcesIfNeeded(context)
  resources += AddServiceEndpointIfNeeded(context)
  return resources


def GenerateOutputList(context, resource_list):
  """Returns list of outputs generated by this module."""
  vm_res = resource_list[0]
  outputs = [{
      'name': 'internalIP',
      'value': '$(ref.%s.networkInterfaces[0].networkIP)' % vm_res['name'],
  }]
  external_ips = context.properties.get(EXTERNAL_IPS, [])
  if external_ips and external_ips[0] != 'NONE':
    outputs.append({
        'name': 'ip',
        'value': ('$(ref.%s.networkInterfaces[0].accessConfigs[0].natIP)' %
                  vm_res['name']),
    })
  return outputs


@common.FormatErrorsDec
def GenerateConfig(context):
  """Generates YAML resource configuration."""
  resource_list = GenerateResourceList(context)
  output_list = GenerateOutputList(context, resource_list)
  return common.MakeResource(resource_list, output_list)
