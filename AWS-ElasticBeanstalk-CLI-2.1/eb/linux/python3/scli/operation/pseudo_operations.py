#!/usr/bin/env python
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
import logging as _logging
import time as _time

from lib.rds import rds_utils
from scli import prompt
from scli.constants import ParameterName
from scli.constants import RdsDefault
from scli.constants import ServiceDefault
from scli.exception import EBSCliException
from scli.operation.base import OperationBase
from scli.operation.base import OperationResult
from scli.resources import AskConfirmationOpMessage
from scli.resources import CommandType
from scli.terminal.base import TerminalBase
log = _logging.getLogger('cli.op')

class ValidateParameterOperation(OperationBase):
    ''' Validate all required parameters and verify all have value'''
    _input_parameters = set()
    
    _output_parameters = set()
    
    def execute(self, parameter_pool):
        
        # Update parameter
        self._update_timeout_thresholds(parameter_pool)
        
        # Checking parameters
        required_params = self._operation_queue.required_parameters
        missing_params = required_params - parameter_pool.parameter_names 
        if len(missing_params) > 0:
            raise EBSCliException('Missing required parameter. "{0}"'.format(missing_params))
        
        log.debug('Finished gathering required parameter')

        ret_result = OperationResult(self, None, None, None)
        return ret_result

    
    def _update_timeout_thresholds(self, parameter_pool):
        parameter_pool.update(ParameterName.WaitForFinishTimeout,
                              parameter_pool.get_value(ParameterName.WaitForFinishTimeout)\
                                + self._rds_time_out(parameter_pool))

        parameter_pool.update(ParameterName.WaitForUpdateTimeout,
                              parameter_pool.get_value(ParameterName.WaitForUpdateTimeout)\
                                + self._rds_time_out(parameter_pool))

    
    def _rds_time_out(self, parameter_pool):
        if parameter_pool.has(ParameterName.RdsEnabled)\
            and parameter_pool.get_value(ParameterName.RdsEnabled):
            return ServiceDefault.RDS_ADDITION_TIMEOUT_IN_SEC
        else:
            return 0
            
    
class AskConfirmationOperation(OperationBase):
    ''' Ask for user's confirmation'''
    _input_parameters = set()
    
    _output_parameters = set()    
    

    def execute(self, parameter_pool):
        
        command = parameter_pool.get_value(ParameterName.Command)
        
        if parameter_pool.has(ParameterName.ApplicationName)\
            and parameter_pool.has(ParameterName.EnvironmentName):
            
            app_name = parameter_pool.get_value(ParameterName.ApplicationName)
            env_name = parameter_pool.get_value(ParameterName.EnvironmentName)
            policy = rds_utils.is_rds_delete_to_snapshot(parameter_pool, app_name, env_name)
            local_rds_switch = parameter_pool.get_value(ParameterName.RdsEnabled)
            if policy is not None and not RdsDefault.del_policy_to_bool(policy):
                if command == CommandType.UPDATE:
                    if local_rds_switch:
                        pass
                    else:
                        prompt.result(AskConfirmationOpMessage.CommandWarning[command])
                else:
                    prompt.result(AskConfirmationOpMessage.CommandWarning[command])
        
        if (parameter_pool.has(ParameterName.Force) \
                and parameter_pool.get_value(ParameterName.Force) == ServiceDefault.ENABLED) \
            or TerminalBase.ask_confirmation(AskConfirmationOpMessage.CommandConfirmation[command]):
            ret_result = OperationResult(self, None, None, None)
            return ret_result
        else:
            log.info('User cancelled command.')
            raise EBSCliException()
        
        
class SleepOperation(OperationBase):
    ''' Idel sleep'''
    _input_parameters = set()
    
    _output_parameters = set()    

    def execute(self, parameter_pool):
        create_request_id = parameter_pool.get_value(ParameterName.CreateEnvironmentRequestID)\
            if parameter_pool.has(ParameterName.CreateEnvironmentRequestID) else None
        delay = ServiceDefault.CREATE_ENV_POLL_DELAY if create_request_id is not None else 0
        _time.sleep(delay)
                 
        ret_result = OperationResult(self, None, None, None)
        return ret_result
    

    