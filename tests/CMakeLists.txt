cmake_minimum_required(VERSION 3.0)
project(test_valgrind_ci)
find_package(PythonInterp)
enable_testing()
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/test.py.in test.py)
add_test(NAME test_basic COMMAND ${PYTHON_EXECUTABLE} -B test.py)
add_executable(test_basic test.c)
