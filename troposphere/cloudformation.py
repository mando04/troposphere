# Copyright (c) 2013, Mark Peek <mark@peek.org>
# All rights reserved.
#
# See LICENSE file for full license.

from . import AWSHelperFn, AWSObject, AWSProperty, Ref
from .validators import integer, boolean, encoding


class Stack(AWSObject):
    resource_type = "AWS::CloudFormation::Stack"

    props = {
        'NotificationARNs': ([basestring], False),
        'Parameters': (dict, False),
        'TemplateURL': (basestring, True),
        'TimeoutInMinutes': (integer, False),
    }


class WaitCondition(AWSObject):
    resource_type = "AWS::CloudFormation::WaitCondition"

    props = {
        'Count': (integer, False),
        'Handle': (Ref, True),
        'Timeout': (integer, True),
    }


class WaitConditionHandle(AWSObject):
    resource_type = "AWS::CloudFormation::WaitConditionHandle"

    props = {}


class Metadata(AWSHelperFn):
    def __init__(self, *args):
        self.data = args

    def JSONrepr(self):
        t = []
        for i in self.data:
            t += i.JSONrepr().items()
        return dict(t)


class InitFileContext(AWSHelperFn):
    def __init__(self, data):
        self.data = data

    def JSONrepr(self):
        return self.data


class InitFile(AWSProperty):
    props = {
        'content': (basestring, False),
        'mode': (basestring, False),
        'owner': (basestring, False),
        'encoding': (encoding, False),
        'group': (basestring, False),
        'source': (basestring, False),
        'authentication': (basestring, False),
        'context': (InitFileContext, False)
    }


class InitFiles(AWSHelperFn):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        for k in data:
            if not isinstance(data[k], InitFile):
                raise ValueError("File '" + k + "' must be of type InitFile")

    def JSONrepr(self):
        return self.data


class InitService(AWSProperty):
    props = {
        'ensureRunning': (boolean, False),
        'enabled': (boolean, False),
        'files': (list, False),
        'packages': (dict, False),
        'sources': (list, False),
        'commands': (list, False)
    }


class InitServices(AWSHelperFn):
    def __init__(self, data):
        self.validate(data)
        self.data = data

    def validate(self, data):
        for k in data:
            if not isinstance(data[k], InitService):
                raise ValueError(
                    "Service '" + k + "' must be of type InitService"
                )

    def JSONrepr(self):
        return self.data


class InitConfigSets(AWSHelperFn):
    def __init__(self, **kwargs):
        self.validate(dict(kwargs))
        self.data = kwargs

    def validate(self, config_sets):
        for k, v in config_sets.iteritems():
            if not isinstance(v, list):
                raise ValueError('configSets values must be of type list')

    def JSONrepr(self):
        return self.data


class InitConfig(AWSProperty):
    props = {
        'groups': (dict, False),
        'users': (dict, False),
        'sources': (dict, False),
        'packages': (dict, False),
        'files': (dict, False),
        'commands': (dict, False),
        'services': (dict, False)
    }


def validate_authentication_type(auth_type):
    valid_types = ['S3', 'basic']
    if auth_type not in valid_types:
        raise ValueError('Type needs to be one of %r' % valid_types)
    return auth_type


class AuthenticationBlock(AWSProperty):
    props = {
        "accessKeyId": (basestring, False),
        "buckets": ([basestring], False),
        "password": (basestring, False),
        "secretKey": (basestring, False),
        "type": (validate_authentication_type, False),
        "uris": ([basestring], False),
        "username": (basestring, False),
        "roleName": (basestring, False)
    }


class Authentication(AWSHelperFn):
    def __init__(self, data):
        self.validate(data)
        self.data = {"AWS::CloudFormation::Authentication": data}

    def validate(self, data):
        for k, v in data.iteritems():
            if not isinstance(v, AuthenticationBlock):
                raise ValueError(
                    'authentication block must be of type'
                    ' cloudformation.AuthenticationBlock'
                )

    def JSONrepr(self):
        return self.data


class Init(AWSHelperFn):
    def __init__(self, data, **kwargs):
        self.validate(data, dict(kwargs))

        if isinstance(data, InitConfigSets):
            self.data = {
                'AWS::CloudFormation::Init': dict({'configSets': data},
                                                  **kwargs)
            }
        else:
            self.data = {'AWS::CloudFormation::Init': data}

    def validate(self, data, config_sets):
        if isinstance(data, InitConfigSets):
            for k, v in sorted(config_sets.iteritems()):
                if not isinstance(v, InitConfig):
                    raise ValueError(
                        'init configs must of type ',
                        'cloudformation.InitConfigSet'
                    )
        else:
            if 'config' not in data:
                raise ValueError('config property is required')
            if not isinstance(data['config'], InitConfig):
                raise ValueError(
                    'config property must be of type cloudformation.InitConfig'
                )

    def JSONrepr(self):
        return self.data
