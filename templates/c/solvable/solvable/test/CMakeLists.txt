find_package(CMocka REQUIRED)

include_directories ("${PROJECT_SOURCE_DIR}/src")
add_executable(apptest test.c)
add_dependencies(apptest apptest)
add_test(apptest apptest)
target_link_libraries(apptest app ${CMOCKA_LIBRARY})