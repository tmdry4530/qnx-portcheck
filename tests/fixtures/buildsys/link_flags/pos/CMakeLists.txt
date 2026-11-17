cmake_minimum_required(VERSION 3.20)
project(sample)
target_link_libraries(app PRIVATE pthread) # EXPECT: LNX-LINK-FLAGS
