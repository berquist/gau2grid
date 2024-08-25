cmake_minimum_required(VERSION 3.15)

project(gau2grid
        VERSION 3.0.0
        LANGUAGES C)
set(gau2grid_AUTHORS      "Daniel G. A. Smith")
set(gau2grid_DESCRIPTION  "Fast computation of a gaussian and its derivative on a grid")
set(gau2grid_URL          "https://github.com/dgasmith/gau2grid")
set(gau2grid_LICENSE      "BSD 3-clause")

list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)


#############################  Options: Build How?  #############################
include(psi4OptionsTools)
option_with_default(MAX_AM "The maximum gaussian angular momentum to compile" 8)
option_with_default(CMAKE_BUILD_TYPE "Build type (Release or Debug)" Release)
if(CMAKE_CXX_COMPILER_ID MATCHES Intel)
option_with_flags(ENABLE_XHOST "Enables processor-specific optimization (with MSVC, it enables AVX2 instructions)" ON
                  "-xHost" "-march=native" "/arch:AVX2")
else()
option_with_flags(ENABLE_XHOST "Enables processor-specific optimization (with MSVC, it enables AVX2 instructions)" ON
                  "-march=native" "-xHost" "/arch:AVX2")
endif()
option_with_default(BUILD_FPIC "Libraries will be compiled with position independent code" ON)
option_with_print(BUILD_SHARED_LIBS "Build final library as shared, not static" ON)
option_with_default(ENABLE_GENERIC "Enables mostly static linking of system libraries for shared library" OFF)
option_with_default(DISABLE_PRAGMA "Disable certain pragma optimizations, appends _GG_NO_PRAGMA to compile flags" OFF )

# Warnings
if((${BUILD_SHARED_LIBS}) AND NOT ${BUILD_FPIC})
    message(FATAL_ERROR "BUILD_SHARED_LIBS ON and BUILD_FPIC OFF are incompatible, as shared library requires position independent code")
endif()

# Install
option_with_default(CMAKE_INSTALL_LIBDIR "Directory to which libraries installed" lib)

########################  Process & Validate Options  ##########################
include(autocmake_safeguards)
include(custom_color_messages)
include(custom_static_library)

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX "/usr/local/gau2grid" CACHE PATH "Install path" FORCE)
endif()
message(STATUS "gau2grid install: ${CMAKE_INSTALL_PREFIX}")

#  <<  Python  >>
find_package(Python3 3.8 REQUIRED COMPONENTS Interpreter Development)
message(STATUS "${Cyan}Found Python ${Python3_VERSION}${ColourReset}: ${Python3_EXECUTABLE}")


################################  Main Project  ################################
add_custom_command(
    OUTPUT  gau2grid/gau2grid.h gau2grid_orbital.c gau2grid_phi.c gau2grid_deriv1.c gau2grid_deriv2.c gau2grid_deriv3.c gau2grid_transform.c gau2grid_helper.c
    COMMAND ${Python3_EXECUTABLE} -c "import sys; \
                                     sys.path.append('${PROJECT_SOURCE_DIR}'); \
                                     import gau2grid as gg; \
                                     gg.c_gen.generate_c_gau2grid(${MAX_AM}, path='${CMAKE_CURRENT_BINARY_DIR}')"
    DEPENDS gau2grid/c_generator.py
            gau2grid/c_generator.py
            gau2grid/codegen.py
            gau2grid/c_pragma.py
            gau2grid/c_util_generator.py
            gau2grid/c_wrapper.py
            gau2grid/docs_generator.py
            gau2grid/order.py
            gau2grid/python_reference.py
            gau2grid/RSH.py
            gau2grid/utility.py
    VERBATIM)

set(sources_list ${CMAKE_CURRENT_BINARY_DIR}/gau2grid_phi.c
                 ${CMAKE_CURRENT_BINARY_DIR}/gau2grid_orbital.c
                 ${CMAKE_CURRENT_BINARY_DIR}/gau2grid_deriv1.c
                 ${CMAKE_CURRENT_BINARY_DIR}/gau2grid_deriv2.c
                 ${CMAKE_CURRENT_BINARY_DIR}/gau2grid_deriv3.c
                 ${CMAKE_CURRENT_BINARY_DIR}/gau2grid_transform.c
                 ${CMAKE_CURRENT_BINARY_DIR}/gau2grid_helper.c)

add_library(gg ${sources_list})
if ("${CMAKE_C_COMPILER_ID}" STREQUAL "PGI")
    set_target_properties(gg PROPERTIES COMPILE_FLAGS "-c11")
else()
    set_target_properties(gg PROPERTIES COMPILE_FLAGS "-std=c11")
endif()
set_target_properties(gg PROPERTIES POSITION_INDEPENDENT_CODE ${BUILD_FPIC}
                                    SOVERSION 2)  # bump whenever interface has changes or removals

if( DISABLE_PRAGMA )
  target_compile_definitions( gg PRIVATE $<BUILD_INTERFACE:__GG_NO_PRAGMA> )
endif()

find_package(StandardMathLibraryC)
target_link_libraries(gg PRIVATE ${STANDARD_MATH_LIBRARY})

if(${BUILD_SHARED_LIBS})
    target_link_libraries(gg PRIVATE ${LIBC_INTERJECT})
endif()


###################################  Install  ##################################
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

set(PN ${PROJECT_NAME})

# Alias to allow for consistent manipulation as a subproject
add_library( ${PN}::gg ALIAS gg )

target_include_directories(gg PUBLIC
                           $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>
                           $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

# GNUInstallDirs "DATADIR" wrong here; CMake search path wants "share".
set(CMAKECONFIG_INSTALL_DIR "share/cmake/${PN}")
configure_package_config_file(cmake/${PN}Config.cmake.in
                              "${CMAKE_CURRENT_BINARY_DIR}/${PN}Config.cmake"
                              INSTALL_DESTINATION ${CMAKECONFIG_INSTALL_DIR})
write_basic_package_version_file(${CMAKE_CURRENT_BINARY_DIR}/${PN}ConfigVersion.cmake
                                 VERSION ${${PN}_VERSION}
                                 COMPATIBILITY SameMajorVersion)

# Install our files
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/gau2grid/gau2grid.h
              ${CMAKE_CURRENT_BINARY_DIR}/gau2grid/gau2grid_pragma.h
              DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PN})

install(TARGETS gg
        EXPORT "${PN}Targets"
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/${PN}Config.cmake
              ${CMAKE_CURRENT_BINARY_DIR}/${PN}ConfigVersion.cmake
        DESTINATION ${CMAKECONFIG_INSTALL_DIR})
install(EXPORT "${PN}Targets"
        NAMESPACE "${PN}::"
        DESTINATION ${CMAKECONFIG_INSTALL_DIR})
export(EXPORT "${PN}Targets"
       NAMESPACE "${PN}::"
       FILE "${PROJECT_BINARY_DIR}/${PN}Targets.cmake")
