# nagiosxi_plugin_template
Template for creating NagiosXI monitoring plugins written in Python.

## Description
This template as a starting point for the development of monitoring plugins for use with NagiosXI. 
The plugin is a working example that will randomly generate an integer between 50 and 100 to be evaluated 
against the thresholds provided at runtime.

### Features
  * The plugin provides limited implementation of critical and warning threshold ranges as per the Nagios Plugin Development Guidelines.
  * The plugin generates optional Nagios formatted performance data.
  * Includes a Python HTTP Requests library based generic function for interacting with the NagiosXI API version 1.
  * Includes a Python HTTP Requests library based generic function for interacting with the NagiosXI API Version 2.
  * Provides an example how to store nagios instance information, and credentials in an external yaml file.
  * Includes generic Python HTTP Requests library based examples for interacting with external API endpoints.
   
