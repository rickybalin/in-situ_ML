project(FortranClient)

cmake_minimum_required(VERSION 3.10)

enable_language(Fortran)

set(CMAKE_BUILD_TYPE Release)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_STANDARD 99)

find_package(MPI)

find_package(Torch REQUIRED)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS} -Wl,--no-as-needed")

include_directories(SYSTEM
    /usr/local/include
    ${MPI_INCLUDE_PATH}
)

# build executables
add_executable(clientFtn.exe
	inference_torch.f
        inference_cpp_bridge.F90
	torch_inf.cpp
)
target_link_libraries(clientFtn.exe
	MPI::MPI_Fortran
        "${TORCH_LIBRARIES}" -lmkl_gf_lp64 -lmkl_gnu_thread
)


