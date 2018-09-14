
#include "ltalloc.h"
#include <benchmark.h>

int
benchmark_initialize() {
	return 0;
}

int
benchmark_finalize(void) {
	return 0;
}

int
benchmark_thread_initialize(void) {
	return 0;
}

int
benchmark_thread_finalize(void) {
	return 0;
}

void
benchmark_thread_collect(void) {
}

void*
benchmark_malloc(size_t alignment, size_t size) {
	return ltmemalign(alignment, size);
}

extern void
benchmark_free(void* ptr) {
	ltfree(ptr);
}

const char*
benchmark_name(void) {
	return "ltalloc";
}
