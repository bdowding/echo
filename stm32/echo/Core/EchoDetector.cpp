#include "EchoDetector.h"

#include "main.h"


EchoDetector::EchoDetector(GPIO_TypeDef* triggerPort, uint16_t triggerPin,
		GPIO_TypeDef* echoPort, uint16_t echoPin)
: _triggerPort(triggerPort)
, _triggerPin(triggerPin)
, _echoPort(echoPort)
, _echoPin(echoPin)
{
}

EchoDetector::~EchoDetector() {
}

bool EchoDetector::SetState(uint32_t onTime, uint32_t offTime)
{
	bool on = onTime == 0;
	HAL_GPIO_WritePin(LD1_GPIO_Port, LD1_Pin, on ? GPIO_PIN_RESET : GPIO_PIN_SET);
	return on;
}
