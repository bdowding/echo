#pragma once


#include <tuple>
#include <span>
#include <functional>
#include <optional>
#include <string.h>

template <class TDest>
std::optional<size_t> BufferToElement(TDest& element, std::span<const uint8_t> source)
{
	if (source.size() < sizeof(element)) {
		// Not enough source data to create a TDest
		return std::nullopt;
	}

	memcpy(&element, source.data(), sizeof(element));
	return sizeof(element);
}

template <class TTuple, int NElement, typename std::enable_if<(NElement == std::tuple_size<TTuple>::value), bool>::type = true>
bool BufferToTuple(TTuple& tuple, std::span<const uint8_t> args)
{
    // Nothing left to parse
    return true;
}

template <class TTuple, int NElement, typename std::enable_if<(NElement < std::tuple_size<TTuple>::value), bool>::type = true>
bool BufferToTuple(TTuple& tuple, std::span<const uint8_t> args)
{
    auto& element = std::get<NElement>(tuple);

    auto result = BufferToElement(element, args);
    if (!result.has_value()) {
    	return false;
    }

	return BufferToTuple<TTuple, NElement + 1>(tuple, args.subspan(0,  args.size() - *result));
}

template <class TClass, class TRet, class TMethodPtr, class TArgsTuple,
    typename std::enable_if<!std::is_same<TRet, void>::value, bool>::type = true, class... TFnArgs>
size_t InvokeFromTuple(TClass& instance, TMethodPtr method, std::span<uint8_t>& output, TArgsTuple& tuple)
{
    // Non-void-return specializiation
    const TRet functionReturnValue = std::apply(std::bind_front(method, instance), tuple);;
    if (sizeof(TRet) > output.size()) {
    	return 0;
    }
    memcpy(output.data(), &functionReturnValue, sizeof(TRet));
    output.subspan(0, sizeof(TRet));
	return sizeof(TRet);
}

template <class TClass, class TRet, class TMethodPtr, class TArgsTuple,
    typename std::enable_if<std::is_same<TRet, void>::value, bool>::type = true, class... TFnArgs>
size_t InvokeFromTuple(TClass& instance, TMethodPtr method, std::span<uint8_t>& output, TArgsTuple& tuple)
{
    // Void-return specializiation
	std::apply(std::bind_front(method, instance), tuple);
    return 0;
}

// Example use:
// TestClass tc;
// BufferInvokeResult ret1 = CallMemberFromArray(&TestClass::ValuesInValuesOut, tc,
//                                                      std::span<const uint8_t>(argBuffer, 8),
//                                                      std::span<uint8_t>(outputBuffer, 8));
template <class TRet, class TClass, class ...TFnArgs>
size_t CallMemberFromArray(TRet(TClass::* fn)(TFnArgs...), TClass& inst, std::span<const uint8_t> args, std::span<uint8_t> output)
{
    // This will be unused for parameterless RPCs.
    std::tuple<TFnArgs...> argsTuple __attribute__((unused));;
    bool parseOk = BufferToTuple<std::tuple<TFnArgs...>, 0>(argsTuple, args);

    if (!parseOk) {
        return 0;
    }

    typedef TRet(TClass::* fnPtrType)(TFnArgs...);
    size_t bytesConsumed = InvokeFromTuple<TClass, TRet, fnPtrType, std::tuple<TFnArgs...>>(inst, fn, output, argsTuple);

    return bytesConsumed;
}

template <class TRet, class TClass, class ...TFnArgs>
size_t CallMemberFromArray(TRet(TClass::* fn)(TFnArgs...) const, const TClass& inst, std::span<const uint8_t> args, std::span<uint8_t> output)
{
    // Just cast away the consts so we can use the existing template.
    TRet(TClass::* fnNonConst)(TFnArgs...) = reinterpret_cast<TRet(TClass::*)(TFnArgs...)>(fn);
    TClass& instNonConst = const_cast<TClass&>(inst);

    return CallMemberFromArray(fnNonConst, instNonConst, args, output);
}
