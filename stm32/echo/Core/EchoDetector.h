#pragma once

#include <stdint.h>

class EchoDetector {
public:
	EchoDetector(GPIO_TypeDef* triggerPort, uint16_t triggerPin,
			GPIO_TypeDef* echoPort, uint16_t echoPin);
	virtual ~EchoDetector();

	bool SetState(uint32_t onTime, uint32_t offTime);

private:
	GPIO_TypeDef* _triggerPort;
	uint16_t _triggerPin;
	GPIO_TypeDef* _echoPort;
	uint16_t _echoPin;
};

