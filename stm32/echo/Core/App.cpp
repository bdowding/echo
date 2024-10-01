#include "App.h"
#include "InvokeFromBuffer.h"
#include "usbd_cdc_if.h"
#include <optional>
#include <stdint.h>
#include <string>
#include <span>
#include "EchoDetector.h"

namespace {
	std::optional<App> TheApp;
}

extern "C" void StartApp() {
	TheApp.emplace();
}

void (App::*usbReceivedHook)(uint8_t *buf, uint32_t *len) = nullptr;

extern "C" void OnUsbDataReceived(uint8_t *buf, uint32_t *len) {
	((*TheApp).*usbReceivedHook)(buf, len);
}

App::App()
: _appTask_attributes {
		.name = "appTask",
		.cb_mem = &_appTaskControlBlock,
		.cb_size = sizeof(_appTaskControlBlock),
		.stack_mem = _appTaskBuffer.data(),
		.stack_size = _appTaskBuffer.size(),
		.priority = (osPriority_t) osPriorityNormal, }
{
	usbReceivedHook = &App::UsbReceived;
	_appTaskHandle = osThreadNew(App::StaticMain, this, &_appTask_attributes);
	std::vector<int> a;
}

App::~App() {

}

void App::StaticMain(void *pAppHandle)
{
	App* pApp = reinterpret_cast<App*>(pAppHandle);
	pApp->ThreadMain();
}

void App::ThreadMain()
{
	while (true) {
		vTaskDelay(10);
	}
}

void App::UsbReceived(uint8_t* buf, uint32_t* recv_len)
{
	if (*recv_len < 1) {
		return;
	}

	std::span<const uint8_t> input_span(buf, *recv_len);

	size_t rvalBytes = CallMemberFromArray(&EchoDetector::SetState, _led, input_span, _sendBuffer);

	CDC_Transmit_FS(_sendBuffer.data(), rvalBytes);
}
