#pragma once

#include "FreeRTOS.h"
#include "cmsis_os2.h"
#include "task.h"
#include <array>
#include "EchoDetector.h"

class App {
public:
	App();
	virtual ~App();

private:
	static void StaticMain(void *pAppHandle);

	void ThreadMain();
	void UsbReceived(uint8_t* buf, uint32_t* len);

	osThreadId_t _appTaskHandle;
	std::array<uint32_t, 512> _appTaskBuffer;
	StaticTask_t _appTaskControlBlock;
	const osThreadAttr_t _appTask_attributes;

	std::array<uint8_t, 64> _sendBuffer;

	EchoDetector _led;
};

