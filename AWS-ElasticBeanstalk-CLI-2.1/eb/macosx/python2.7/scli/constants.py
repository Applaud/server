#!/usr/bin/env python
# -*- coding: utf-8 -*-
#==============================================================================
# Copyright 2012 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use
# this file except in compliance with the License. A copy of the License is
# located at
#
#       http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or
# implied. See the License for the specific language governing permissions
# and limitations under the License.
#==============================================================================

from lib.utility.basetype import ValuedEnum
from lib.utility.basetype import OrderedEnum


#----------------------------------------------
# Parameters
#----------------------------------------------
# Standard name of parameters used in Elastic Beanstalk Command Line Interface
ParameterName = ValuedEnum({
    u'Command' : 0,
    
    u'AwsAccessKeyId' : 11,
    u'AwsSecretAccessKey' : 12,
    u'AwsCredentialFile' : 13,
    
    u'Region' : 21,
    u'ServiceEndpoint' :22,
    
    u'ApplicationName': 101,
    u'ApplicationVersionName':111,
    u'EnvironmentName':121,
    u'EnvironmentId':122,
    
    u'SolutionStack' : 201,
    u'OriginalSolutionStack' : 202,
    
    u'OptionSettingFile' : 501,
    
    u'RdsEnabled': 601,
    u'RdsEndpoint': 602,
    u'RdsSnippetUrl': 603,
    u'RdsSourceSnapshotName': 606,
    u'RdsEngine': 611,
    u'RdsEngineVersion': 612,
    u'RdsInstanceClass': 613,
    u'RdsMultiAZ': 614,
    u'RdsLicenseModel': 615,
    u'RdsAllocatedStorage': 616,
    u'RdsInstanceName': 621,
    u'RdsMasterUsername': 622,
    u'RdsMasterPassword': 623,
    u'RdsDbName' : 631,    
    u'RdsDeletionPolicy': 651,
    
    u'ServiceConnectionTimeout' : 1001,
    u'ServiceRetryThreshold' : 1011,
    u'Force' : 1021,
    
    u'Verbose' : 1051,
    
    u'WaitForFinishTimeout': 1101,
    u'WaitForUpdateTimeout': 1102,
    u'PollDelay' : 1201,
    
    u'CreateEnvironmentRequestID' : 2001,
    u'TerminateEnvironmentRequestID' : 2002,
    u'UpdateEnvironmentRequestID' : 2002,
    
    u'AvailableSolutionStacks': 2101
})


# Source of parameter value
ParameterSource = ValuedEnum({ 
    u'CliArgument' : 0,
    u'Terminal' : 1,
    u'ConfigFile' : 2,
    u'OsEnvironment' : 3,
    u'OperationOutput' : 4,
    u'Default' : 10,
})


#----------------------------------------------
# Terminal
#----------------------------------------------
class TerminalConstant(object):
    Y = u'Y'
    Yes = u'Yes'
    N = u'N'
    No = u'No'
    TRUE = u'True'
    FALSE = u'False'

    RdsSnapshotListNumber = 5
    

#----------------------------------------------
# Services
#----------------------------------------------
ServiceRegion = OrderedEnum([
    u'UsEast1',
    u'UsWest1',
    u'UsWest2',
    u'EuWest1',
    u'ApNortheast1',
    u'ApSoutheast1',
    u'SaEast1',
])

AvailableServiceRegion = [
   ServiceRegion.UsEast1,
   ServiceRegion.UsWest2,
   ServiceRegion.UsWest1,
   ServiceRegion.EuWest1,
   ServiceRegion.ApNortheast1,
]


ServiceRegionName = {
    ServiceRegion.ApNortheast1 : u'Asia Pacific (Tokyo)',
    ServiceRegion.ApSoutheast1 : u'Asia Pacific (Singapore)',
    ServiceRegion.EuWest1: u'EU West (Ireland)',
    ServiceRegion.SaEast1: u'S. America (Sao Paulo)',
    ServiceRegion.UsEast1 : u'US East (Virginia)',
    ServiceRegion.UsWest1 : u'US West (North California)',
    ServiceRegion.UsWest2 : u'US West (Oregon)',
}

ServiceRegionId = {
    ServiceRegion.ApNortheast1 : u'ap-northeast-1',
    ServiceRegion.ApSoutheast1 : u'ap-southeast-1',
    ServiceRegion.EuWest1: u'eu-west-1',    
    ServiceRegion.SaEast1: u'sa-east-1',
    ServiceRegion.UsEast1 : u'us-east-1',
    ServiceRegion.UsWest1 : u'us-west-1',
    ServiceRegion.UsWest2 : u'us-west-2',
}

ServiceEndpoint = {
    ServiceRegion.ApNortheast1 : u'https://elasticbeanstalk.ap-northeast-1.amazonaws.com',
    ServiceRegion.ApSoutheast1 : u'https://elasticbeanstalk.ap-southeast-1.amazonaws.com',
    ServiceRegion.EuWest1: u'https://elasticbeanstalk.eu-west-1.amazonaws.com',
    ServiceRegion.SaEast1: u'https://elasticbeanstalk.sa-east-1.amazonaws.com',
    ServiceRegion.UsEast1 : u'https://elasticbeanstalk.us-east-1.amazonaws.com',
    ServiceRegion.UsWest1 : u'https://elasticbeanstalk.us-west-1.amazonaws.com',
    ServiceRegion.UsWest2 : u'https://elasticbeanstalk.us-west-2.amazonaws.com',
}

SnippetBucket = {
    ServiceRegion.ApNortheast1 : u'https://s3.amazonaws.com/elasticbeanstalk-env-resources-ap-northeast-1/eb_snippets',
    ServiceRegion.ApSoutheast1 : u'https://s3.amazonaws.com/elasticbeanstalk-env-resources-ap-southeast-1/eb_snippets',
    ServiceRegion.EuWest1 : u'https://s3.amazonaws.com/elasticbeanstalk-env-resources-eu-west-1/eb_snippets',
    ServiceRegion.SaEast1 : u'https://s3.amazonaws.com/elasticbeanstalk-env-resources-sa-east-1/eb_snippets',
    ServiceRegion.UsEast1 : u'https://s3.amazonaws.com/elasticbeanstalk-env-resources-us-east-1/eb_snippets',
    ServiceRegion.UsWest1 : u'https://s3.amazonaws.com/elasticbeanstalk-env-resources-us-west-1/eb_snippets',
    ServiceRegion.UsWest2 : u'https://s3.amazonaws.com/elasticbeanstalk-env-resources-us-west-2/eb_snippets',
}

#----------------------------------------------
# Solution stacks and sample app
#----------------------------------------------

class DefualtAppSource(object):
    Namespace = u'aws:cloudformation:template:parameter'
    OptionName = u'AppSource' 

TomcatSampleAppFile = u'elasticbeanstalk-sampleapp.war'
PhpSampleAppFile = u'php-sample.zip'
IisSampleAppFile = u'FirstSample.zip'

ApNortheast1SampleBucket = u'elasticbeanstalk-samples-ap-northeast-1'
ApSoutheast1SampleBucket = u'elasticbeanstalk-samples-ap-southeast-1-1'
EuWest1SampleBucket = u'elasticbeanstalk-samples-eu-west-1'
SaEast1SampleBucket = u'elasticbeanstalk-samples-sa-east-1'
UsEast1SampleBucket = u'elasticbeanstalk-samples-us-east-1'
UsWest1SampleBucket = u'elasticbeanstalk-samples-us-west-1'
UsWest2SampleBucket = u'elasticbeanstalk-samples-us-west-2'


class TomcatAppContainer(object):
    Name = u'Tomcat'
    Regex = u'^(32|64)bit Amazon Linux running Tomcat (6|7)(( (L|l)egacy)|( \((L|l)egacy\)))?$'
    
class PhpAppContainer(object):
    Name = u'PHP'
    Regex = u'^(32|64)bit Amazon Linux running PHP 5.3(( (L|l)egacy)|( \((L|l)egacy\)))?$'

class IisAppContainer(object):
    Name = u'IIS'
    Regex = u'^64bit Windows Server 2008 R2 running IIS 7.5(( (L|l)egacy)|( \((L|l)egacy\)))?$'

class PythonAppContainer(object):
    Name = u'Python'
    Regex = u'^(32|64)bit Amazon Linux running Python$'


KnownAppContainers = {
    TomcatAppContainer,
    PhpAppContainer,
    IisAppContainer,
    PythonAppContainer,
}

DefaultVersionS3Location = {
    TomcatAppContainer.Name : {
        ServiceRegion.ApNortheast1 :(ApNortheast1SampleBucket, 
                                     TomcatSampleAppFile),
        ServiceRegion.ApSoutheast1 :(ApSoutheast1SampleBucket, 
                                     TomcatSampleAppFile),
        ServiceRegion.EuWest1 :(EuWest1SampleBucket, 
                                TomcatSampleAppFile),
        ServiceRegion.SaEast1 :(SaEast1SampleBucket, 
                                TomcatSampleAppFile),
        ServiceRegion.UsEast1 :(UsEast1SampleBucket, 
                                TomcatSampleAppFile),
        ServiceRegion.UsWest1 :(UsWest1SampleBucket, 
                                TomcatSampleAppFile),
        ServiceRegion.UsWest2 :(UsWest2SampleBucket, 
                                TomcatSampleAppFile),                               
    },
    PhpAppContainer.Name : {
        ServiceRegion.ApNortheast1 :(ApNortheast1SampleBucket, 
                                     PhpSampleAppFile),
        ServiceRegion.ApSoutheast1 :(ApSoutheast1SampleBucket, 
                                     PhpSampleAppFile),
        ServiceRegion.EuWest1 :(EuWest1SampleBucket, 
                                PhpSampleAppFile),
        ServiceRegion.SaEast1 :(SaEast1SampleBucket, 
                                PhpSampleAppFile),
        ServiceRegion.UsEast1 :(UsEast1SampleBucket, 
                                PhpSampleAppFile),
        ServiceRegion.UsWest1 :(UsWest1SampleBucket, 
                                PhpSampleAppFile),
        ServiceRegion.UsWest2 :(UsWest2SampleBucket, 
                                PhpSampleAppFile),
    },
    IisAppContainer.Name : {
        ServiceRegion.ApNortheast1 :(ApNortheast1SampleBucket, 
                                     IisSampleAppFile),
        ServiceRegion.ApSoutheast1 :(ApSoutheast1SampleBucket, 
                                     IisSampleAppFile),
        ServiceRegion.EuWest1 :(EuWest1SampleBucket, 
                                IisSampleAppFile),
        ServiceRegion.SaEast1 :(SaEast1SampleBucket, 
                                IisSampleAppFile),
        ServiceRegion.UsEast1 :(UsEast1SampleBucket, 
                                IisSampleAppFile),
        ServiceRegion.UsWest1 :(UsWest1SampleBucket, 
                                IisSampleAppFile),
        ServiceRegion.UsWest2 :(UsWest2SampleBucket, 
                                IisSampleAppFile),                           
    },
}




#----------------------------------------------
# RDS
#----------------------------------------------

RdsEndpoint = {
    ServiceRegion.ApNortheast1 : u'https://rds.ap-northeast-1.amazonaws.com',
    ServiceRegion.ApSoutheast1 : u'https://rds.ap-southeast-1.amazonaws.com',
    ServiceRegion.EuWest1: u'https://rds.eu-west-1.amazonaws.com',
    ServiceRegion.SaEast1: u'https://rds.sa-east-1.amazonaws.com',
    ServiceRegion.UsEast1 : u'https://rds.amazonaws.com',
    ServiceRegion.UsWest1 : u'https://rds.us-west-1.amazonaws.com',
    ServiceRegion.UsWest2 : u'https://rds.us-west-2.amazonaws.com',
}


class RdsDefault(object):
    PasswordMismatchThreshold = 3
    
    SnippetUrlMask = u'{0}/rds/rds.json'
    SnippetName = u'RdsExtensionEB'
    SnippetAddOrder = 10000
    SnippetRemoveOrder = -1

#    DbName = u'elasticbeanstalk_db'
#    DbIdPostfix = u'-eb'
    DbIdLengthLimit = {
                       u'mysql' : 63,
                       u'sqlserver-ex' : 15,
                       u'sqlserver-se' : 15,
                       u'sqlserver-web' : 15,
                       }
    
    EngineMap = {
        TomcatAppContainer : u'mysql',
        PhpAppContainer : u'mysql',
        IisAppContainer : u'sqlserver-ex',
        PythonAppContainer: u'mysql',                     
    }
    
    DeletionPolicySnapshot = u'Snapshot'
    DeletionPolicyDelete = u'Delete'
    ResourceType = u'AWS::RDS::DBInstance'
    HostnameType = u'Endpoint'
    PortType = u'Port'
    
    @classmethod
    def get_snippet_url(cls, region):
        return cls.SnippetUrlMask.format(SnippetBucket[region])    

    @classmethod
    def bool_to_del_policy(cls, switch):
        if switch:
            return cls.DeletionPolicySnapshot
        else:
            return cls.DeletionPolicyDelete

    @classmethod
    def del_policy_to_bool(cls, policy):
        if policy == cls.DeletionPolicySnapshot:
            return True
        else:
            return False

    Namespace = u'aws:rds:dbinstance'

    OptionNames = {
        ParameterName.RdsEngine : u'DBEngine',
        ParameterName.RdsEngineVersion : u'DBEngineVersion',
        ParameterName.RdsInstanceClass : u'DBInstanceClass',
        ParameterName.RdsAllocatedStorage : u'DBAllocatedStorage',
        ParameterName.RdsMultiAZ : u'MultiAZDatabase',
        ParameterName.RdsLicenseModel : u'DBLicenseModel',
        
        ParameterName.RdsSourceSnapshotName : u'DBSnapshotIdentifier',
        ParameterName.RdsDbName : u'DBName',
        ParameterName.RdsMasterUsername : u'DBUser',
        ParameterName.RdsMasterPassword : u'DBPassword',
        ParameterName.RdsDeletionPolicy : u'DBDeletionPolicy',
    }
         
    OptionMinSet = set({
        ParameterName.RdsEngine,
        ParameterName.RdsSourceSnapshotName,                     
        ParameterName.RdsMasterPassword,
        ParameterName.RdsDeletionPolicy,
    })
    
    PasswordMinSize = 8
    PasswordMaxSize = 41
    
#----------------------------------------------
# Application and environment default
#----------------------------------------------

class EnvironmentStatus(object):
    Launching = u'Launching'
    Ready = u'Ready'
    Updating = u'Updating'
    Terminating = u'Terminating'
    Terminated = u'Terminated'
    
class EnvironmentHealth(object):
    Green = u'Green'
    Yellow = u'Yellow'
    Red = u'Red'
    Grey = u'Grey'
    
class EventSeverity(object):
    Trace = u'TRACE'
    Debug = u'Debug'
    Info = u'INFO'
    Warn = u'WARN'
    Error = u'ERROR'
    Fatal = u'FATAL'      

class ValidationSeverity(object):
    SeverityError = u'error'
    SeverityWarning = u'warning'

class ServiceDefault(object):
    """ Defines CLI related constant values. """
    DEFAULT_VERSION_NAME = u'Sample Application'
    
    class Environment(object):
        REGEX_NAME_FILTER = u'[^A-Za-z0-9\-]+'
        NAME_POSTFIX = u'-env' 
        MAX_NAME_LEN = 23
    
    SERVICE_CALL_MAX_RETRY = 5
    
    CONNECTION_TIMEOUT_IN_SEC = 30   
    WAIT_TIMEOUT_IN_SEC = 600
    UPDATE_TIMEOUT_IN_SEC = 300
    RDS_ADDITION_TIMEOUT_IN_SEC = 300
    
    POLL_DELAY_IN_SEC = 5
    CREATE_ENV_POLL_DELAY = 3
    TERMINATE_ENV_POLL_DELAY = 0
    UPDATE_ENV_POLL_DELAY = 0

    CHAR_CODEC = 'utf-8'
    ENABLED = u'Enabled'
    USER_AGENT = 'eb v2.1.0'

    STATUS_EVENT_LEVEL = EventSeverity.Warn
    STATUS_EVENT_MAX_NUM = 3
  
    
#----------------------------------------------
# Configuration file and log file
#----------------------------------------------

class FileDefaultParameter(object):
    RotationMaxRetry = 1000


class OSSpecific(object):

    '''Windows specific constants'''
    WindowsName = u'Windows'
    WindowsClimbUpDepth = 2
    WindowsModuleScriptPath = u'AWSDevTools\\Windows'
    WindowsModuleScriptName = u'AWSDevTools-OneTimeSetup.bat'
    WindowsRepoScript = u'AWSDevTools\\Windows\\AWSDevTools-RepositorySetup.bat'
    
    
    '''Nix specific constants'''
    LinuxName = u'Linux'     
    LinuxClimbUpDepth = 3
    LinuxRepoScript = u'AWSDevTools/Linux/AWSDevTools-RepositorySetup.sh'


class AwsCredentialFileDefault(object):
    FilePath = u'.elasticbeanstalk'
    FileName = u'aws_credential_file'
    OSVariableName = u'AWS_CREDENTIAL_FILE'
    KeyName = {
        ParameterName.AwsAccessKeyId : u'AWSAccessKeyId',
        ParameterName.AwsSecretAccessKey : u'AWSSecretKey',
        ParameterName.RdsMasterPassword : u'RDSMasterPassword', 
    }


class EbLocalDir(object):
    Path = u'.elasticbeanstalk'
    Name = Path + u'/'
    NameRe = Path + u'/'
    
class EbLogFile(object):
    Name = u'eb-cli.log'
    NameRe = u'.*eb-cli\.log.*'

class EbConfigFile(object):
    Name = u'config'
    NameRe = u'.*\config.*'



class OptionSettingFile(object):
    Name = u'optionsettings'
    NameRe = u'.*\.optionsettings.*'
    
class GitIgnoreFile(object):
    Name = u'.gitignore'
    Path = u'.'
    Files = {
             EbLocalDir,
             }

class DevToolsConfigFile(object):
    Name = u'config'
    Path = u'.git'
    Endpoint = u'git.elasticbeanstalk.{0}.amazonaws.com'
    InitHelpUrl = u'http://docs.amazonwebservices.com/elasticbeanstalk/latest'\
        '/dg/GettingStarted.GetSetup-devtools.html'
    
    SetAccessKey = [u'git', u'config', u'aws.accesskey']
    SetSecretKey = [u'git', u'config', u'aws.secretkey']
    SetRegion = [u'git', u'config', u'aws.region']
    SetServicePoint = [u'git', u'config', u'aws.elasticbeanstalk.host']
    SetApplicationName = [u'git', u'config', u'aws.elasticbeanstalk.application']
    SetEnvironmentName = [u'git', u'config', u'aws.elasticbeanstalk.environment']    


class FileErrorConstant(object):
    FileNotFoundErrorCode = 2
    FileNotFoundErrorMsg = u'No such file or directory'    

OutputLevel = OrderedEnum([
                    u'Info',
                    u'ResultOnly',
                    u'Quiet',
                    u'Silence',
                    ])

class CABundle(object):
    Path = u'.'
    Name = u'ca-bundle.crt'
    
    
#----------------------------------------------
# OptionSettingList
#----------------------------------------------

LocalOptionSettings = {
    u'aws:autoscaling:launchconfiguration' : {
        u'EC2KeyName',
        u'InstanceType', 
    },
    u'aws:elasticbeanstalk:sns:topics' : {
        u'Notification Endpoint', 
        u'Notification Protocol',
    },
    u'aws:elasticbeanstalk:monitoring' : {
        u'Automatically Terminate Unhealthy Instances',
    },
    u'aws:elasticbeanstalk:hostmanager' : {
        u'LogPublicationControl',
    },
    u'aws:elasticbeanstalk:application' : {
        u'Application Healthcheck URL',
    },
    u'aws:autoscaling:asg' : {
        u'MaxSize',
        u'MinSize',
        u'Custom Availability Zones',
    },
    u'aws:rds:dbinstance' : {
        u'DBDeletionPolicy',
        u'DBEngine',
        u'DBSnapshotIdentifier',
        u'DBUser',
    },
}

OptionSettingContainerPrefix = u'aws:elasticbeanstalk:container'

class OptionSettingApplicationEnvironment(object): 
    Namespace = u'aws:elasticbeanstalk:application:environment'
    IgnoreOptionNames = {
        u'AWS_ACCESS_KEY_ID',
        u'AWS_SECRET_KEY',
    }
    
    