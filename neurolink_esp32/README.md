# Neurolink ESP32

ESP32-S3 based project scaffold.

## System Overview
This project targets a tactical command-and-control terminal system with four subsystems:
- Hardware subsystem
- Software subsystem
- Support subsystem
- Network subsystem

## Structure
- `src/` PlatformIO Arduino source
	- `src/subsystems/` subsystem placeholders
		- `hardware/`
		- `software/`
		- `support/`
		- `network/`
			- `software/app_layer/`
			- `software/security_framework/`
			- `software/middleware/`
			- `software/os_layer/`
			- `support/logistics_system/`
			- `support/maintenance_system/`
			- `support/training_system/`
			- `network/data_distribution/`
			- `network/network_management/`
			- `network/protocol_stack/`
			- `hardware/protection_structure/`
			- `hardware/power_management/`
			- `hardware/hmi_unit/`
			- `hardware/communication_module/`
			- `hardware/sensor_suite/`
			- `hardware/core_processing_unit/`

## Notes
- Board: ESP32-S3 DevKitC-1
- Serial: 115200
