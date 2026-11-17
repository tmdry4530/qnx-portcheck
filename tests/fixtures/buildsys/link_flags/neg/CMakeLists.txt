cmake_minimum_required(VERSION 3.20)
# target_link_libraries(app PRIVATE pthread)
target_link_libraries(app PRIVATE Threads::Threads)
