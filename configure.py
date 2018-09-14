#!/usr/bin/env python

"""Ninja build configurator for foundation library"""

import sys
import os

sys.path.insert(0, os.path.join('build', 'ninja'))

import generator

generator = generator.Generator(project = 'rpmalloc', variables = {'bundleidentifier': 'com.rampantpixels.rpmalloc.$(binname)', 'nowarning': True})
target = generator.target
writer = generator.writer
toolchain = generator.toolchain

includepaths = ['test', 'benchmark']
test_lib = generator.lib(module = 'test', sources = ['thread.c', 'timer.c'], includepaths = includepaths)
benchmark_lib = generator.lib(module = 'benchmark', sources = ['main.c'], includepaths = includepaths)

#Build one binary per benchmark
generator.bin(module = 'rpmalloc', sources = ['benchmark.c', 'rpmalloc.c'], binname = 'benchmark-rpmalloc-unlimit', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = ['benchmark', 'test'], includepaths = includepaths, variables = {'defines': ['ENABLE_UNLIMITED_CACHE=1']})
generator.bin(module = 'rpmalloc', sources = ['benchmark.c', 'rpmalloc.c'], binname = 'benchmark-rpmalloc-size', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = ['benchmark', 'test'], includepaths = includepaths, variables = {'defines': ['ENABLE_SPACE_PRIORITY_CACHE=1']})
generator.bin(module = 'rpmalloc', sources = ['benchmark.c', 'rpmalloc.c'], binname = 'benchmark-rpmalloc', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = ['benchmark', 'test'], includepaths = includepaths)
generator.bin(module = 'rpmalloc', sources = ['benchmark.c', 'rpmalloc.c'], binname = 'benchmark-rpmalloc-nocache', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = ['benchmark', 'test'], includepaths = includepaths, variables = {'defines': ['DISABLE_CACHE=1']})

if target.is_android():
	resources = [os.path.join('all', 'android', item) for item in [
		'AndroidManifest.xml', os.path.join('layout', 'main.xml'), os.path.join('values', 'strings.xml'),
		os.path.join('drawable-ldpi', 'icon.png'), os.path.join('drawable-mdpi', 'icon.png'), os.path.join('drawable-hdpi', 'icon.png'),
		os.path.join('drawable-xhdpi', 'icon.png'), os.path.join('drawable-xxhdpi', 'icon.png'), os.path.join('drawable-xxxhdpi', 'icon.png')
	]]
	appsources = [os.path.join('test', 'all', 'android', 'java', 'com', 'rampantpixels', 'foundation', 'test', item) for item in [
		'TestActivity.java'
	]]
	variables = {}
	generator.app(module = '', sources = appsources, binname = 'benchmark-rpmalloc', basepath = '', implicit_deps = [benchmark_lib, test_lib], libs = ['benchmark', 'test'], resources = resources, includepaths = includepaths, variables = variables)

generator.bin(module = 'crt', sources = ['benchmark.c'], binname = 'benchmark-crt', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = ['benchmark', 'test'], includepaths = includepaths)
if not target.is_android():
	generator.bin(module = 'nedmalloc', sources = ['benchmark.c', 'nedmalloc.c'], binname = 'benchmark-nedmalloc', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = ['benchmark', 'test'], includepaths = includepaths)

platform_includepaths = [os.path.join('benchmark', 'ptmalloc3')]
if target.is_windows():
	platform_includepaths += [os.path.join('benchmark', 'ptmalloc3', 'sysdeps', 'windows')]
else:
	platform_includepaths += [os.path.join('benchmark', 'ptmalloc3', 'sysdeps', 'pthread')]
if not target.is_android():
	generator.bin(module = 'ptmalloc3', sources = ['benchmark.c', 'ptmalloc3.c', 'malloc.c'], binname = 'benchmark-ptmalloc3', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = ['benchmark', 'test'], includepaths = includepaths + platform_includepaths)

hoardincludepaths = [
	os.path.join('benchmark', 'hoard', 'include'),
	os.path.join('benchmark', 'hoard', 'include', 'hoard'),
	os.path.join('benchmark', 'hoard', 'include', 'util'),
	os.path.join('benchmark', 'hoard', 'include', 'superblocks'),
	os.path.join('benchmark', 'hoard'),
	os.path.join('benchmark', 'hoard', 'Heap-Layers')
]
hoardsources = ['source/libhoard.cpp']
if target.is_macos() or target.is_ios():
	hoardsources += ['Heap-Layers/wrappers/macwrapper.cpp']
elif target.is_windows():
	hoardsources += ['Heap-Layers/wrappers/winwrapper.cpp']
else:
	hoardsources += ['Heap-Layers/wrappers/gnuwrapper.cpp']
if target.is_macos() or target.is_ios():
	hoardsources += ['source/mactls.cpp']
elif target.is_windows():
	hoardsources += ['source/wintls.cpp']
else:
	hoardsources += ['source/unixtls.cpp']
if not target.is_android():
	hoard_lib = generator.lib(module = 'hoard', sources = hoardsources, basepath = 'benchmark', includepaths = includepaths + hoardincludepaths)
	hoard_depend_libs = ['hoard', 'benchmark', 'test']
	generator.bin(module = 'hoard', sources = ['benchmark.c'], binname = 'benchmark-hoard', basepath = 'benchmark', implicit_deps = [hoard_lib, benchmark_lib, test_lib], libs = hoard_depend_libs, includepaths = includepaths, variables = {'runtime': 'c++'})

gperftoolsincludepaths = [
	os.path.join('benchmark', 'gperftools', 'src'),
	os.path.join('benchmark', 'gperftools', 'src', 'base'),
	os.path.join('benchmark', 'gperftools', 'src', target.get())
]
gperftoolsbasesources = [
	'dynamic_annotations.c', 'linuxthreads.cc', 'logging.cc', 'low_level_alloc.cc', 'spinlock.cc',
	'spinlock_internal.cc', 'sysinfo.cc'
]
if not target.is_windows():
	gperftoolsbasesources += ['thread_lister.c']
gperftoolsbasesources = [os.path.join('src', 'base', path) for path in gperftoolsbasesources]
gperftoolssources = [
	'central_freelist.cc', 'common.cc', 'fake_stacktrace_scope.cc', 'heap-checker.cc', 'heap-profile-table.cc', 'heap-checker-bcad.cc', 'internal_logging.cc',
	'malloc_extension.cc', 'malloc_hook.cc', 'memfs_malloc.cc', 'memory_region_map.cc',
	'page_heap.cc', 'raw_printer.cc', 'sampler.cc',  'stacktrace.cc', 'stack_trace_table.cc',
	'static_vars.cc', 'span.cc', 'symbolize.cc', 'tcmalloc.cc', 'thread_cache.cc'
]
if not target.is_windows():
	gperftoolssources += ['maybe_threads.cc', 'system-alloc.cc']
if target.is_windows():
	gperftoolssources += [os.path.join('windows', 'port.cc'), os.path.join('windows', 'system-alloc.cc')]
gperftoolssources = [os.path.join('src', path) for path in gperftoolssources]
if not target.is_android():
	gperftools_lib = generator.lib(module = 'gperftools', sources = gperftoolsbasesources + gperftoolssources, basepath = 'benchmark', includepaths = includepaths + gperftoolsincludepaths)
	gperftools_depend_libs = ['gperftools', 'benchmark', 'test']
	generator.bin(module = 'gperftools', sources = ['benchmark.c'], binname = 'benchmark-tcmalloc', basepath = 'benchmark', implicit_deps = [gperftools_lib, benchmark_lib, test_lib], libs = gperftools_depend_libs, includepaths = includepaths, variables = {'runtime': 'c++'})

jemallocincludepaths = [
	os.path.join('benchmark', 'jemalloc', 'include'),
	os.path.join('benchmark', 'jemalloc', 'include', 'jemalloc'),
	os.path.join('benchmark', 'jemalloc', 'include', 'jemalloc', 'internal')
]
jemallocsources = [
	'jemalloc.c', 'arena.c', 'base.c', 'bitmap.c', 'ckh.c', 'ctl.c', 'extent.c', 'extent_dss.c',
	'extent_mmap.c', 'hash.c', 'large.c', 'malloc_io.c', 'mutex.c', 'nstime.c', 'pages.c',
	'prng.c', 'prof.c', 'rtree.c', 'stats.c', 'spin.c', 'tcache.c', 'ticker.c', 'tsd.c', 'witness.c'
]
jemallocsources = [os.path.join('src', path) for path in jemallocsources]
if not target.is_windows() and not target.is_android():
	jemalloc_lib = generator.lib(module = 'jemalloc', sources = jemallocsources, basepath = 'benchmark', includepaths = includepaths + jemallocincludepaths)
	jemalloc_depend_libs = ['jemalloc', 'benchmark', 'test']
	generator.bin(module = 'jemalloc', sources = ['benchmark.c'], binname = 'benchmark-jemalloc', basepath = 'benchmark', implicit_deps = [jemalloc_lib, benchmark_lib, test_lib], libs = jemalloc_depend_libs, includepaths = includepaths)

scallocincludepaths = [
	os.path.join('benchmark', 'scalloc', 'src'),
	os.path.join('benchmark', 'scalloc', 'src', 'platform')
]
scallocsources = [
	'glue.cc'
]
scallocsources = [os.path.join('src', path) for path in scallocsources]
if not target.is_windows() and not target.is_android():
	scalloc_lib = generator.lib(module = 'scalloc', sources = scallocsources, basepath = 'benchmark', includepaths = includepaths + scallocincludepaths)
	scalloc_depend_libs = ['scalloc', 'benchmark', 'test']
	generator.bin(module = 'scalloc', sources = ['benchmark.c'], binname = 'benchmark-scalloc', basepath = 'benchmark', implicit_deps = [scalloc_lib, benchmark_lib, test_lib], libs = scalloc_depend_libs, includepaths = includepaths, variables = {'runtime': 'c++'})

lockfree_malloc_depend_libs = ['benchmark', 'test']
if not target.is_android():
	generator.bin(module = 'lockfree-malloc', sources = ['benchmark.c', 'lite-malloc.cpp'], binname = 'benchmark-lockfree-malloc', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = lockfree_malloc_depend_libs, includepaths = includepaths, variables = {'runtime': 'c++'})

bmallocincludepaths = [
	os.path.join('benchmark', 'bmalloc', 'bmalloc')
]
bmallocsources = [
	'Allocator.cpp', 'Cache.cpp', 'Deallocator.cpp', 'DebugHeap.cpp', 'Environment.cpp', 'Heap.cpp',
	'LargeMap.cpp', 'Logging.cpp', 'mbmalloc.cpp', 'ObjectType.cpp', 'StaticMutex.cpp', 'VMHeap.cpp'
]
if target.is_macos() or target.is_ios():
	bmallocsources += ['Zone.cpp']
bmallocsources = [os.path.join('bmalloc', path) for path in bmallocsources]
if not target.is_android():
	bmalloc_lib = generator.lib(module = 'bmalloc', sources = bmallocsources, basepath = 'benchmark', includepaths = includepaths + bmallocincludepaths)
	bmalloc_depend_libs = ['bmalloc', 'benchmark', 'test']
	generator.bin(module = 'bmalloc', sources = ['benchmark.cc'], binname = 'benchmark-bmalloc', basepath = 'benchmark', implicit_deps = [bmalloc_lib, benchmark_lib, test_lib], libs = bmalloc_depend_libs, includepaths = includepaths, variables = {'runtime': 'c++'})

#Requires -mrtm and CPU tsx support for full performance?
supermallocincludepaths = [
	os.path.join('benchmark', 'supermalloc', 'src')
]
supermallocsources = [
	'bassert.cc', 'cache.cc', 'footprint.cc', 'futex_mutex.cc', 'has_tsx.cc', 'huge_malloc.cc',
	'large_malloc.cc', 'makechunk.cc', 'malloc.cc', 'rng.cc', 'small_malloc.cc', 'stats.cc',
	'generated_constants.cc'
]
supermallocsources = [os.path.join('src', path) for path in supermallocsources]
if not target.is_android():
	supermalloc_lib = generator.lib(module = 'supermalloc', sources = supermallocsources, basepath = 'benchmark', includepaths = includepaths + supermallocincludepaths, variables = {'defines': ['USE_PTHREAD_MUTEXES']})
	supermalloc_depend_libs = ['supermalloc', 'benchmark', 'test']
	generator.bin(module = 'supermalloc', sources = ['benchmark.c'], binname = 'benchmark-supermalloc', basepath = 'benchmark', implicit_deps = [supermalloc_lib, benchmark_lib, test_lib], libs = supermalloc_depend_libs, includepaths = includepaths, variables = {'runtime': 'c++'})

if toolchain.name() == "gcc":
	lockless_depend_libs = ['benchmark', 'test']
	if target.is_linux():
		generator.bin(module = 'lockless', sources = ['benchmark.c', 'll_alloc.c'], binname = 'benchmark-lockless', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = lockless_depend_libs, includepaths = includepaths, variables = {'defines': ['USE_PREFIX']})

generator.bin(module = 'ltalloc', sources = ['benchmark.c', 'ltalloc.cc'], binname = 'benchmark-ltalloc', basepath = 'benchmark', implicit_deps = [benchmark_lib, test_lib], libs = ['benchmark', 'test'], includepaths = includepaths)

