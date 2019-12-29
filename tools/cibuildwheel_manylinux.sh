#!/usr/bin/env bash

set -e -x

# compile TBB
cur_dir=`pwd`


export TBB_URL="https://github.com/intel/tbb/archive/2019_U9.zip"

curl -L "${TBB_URL}" -o archive.tgz
unzip archive.tgz
mv tbb* tbb
cd tbb
tbb_dir=`pwd`

make -j tbb

cd build
cd *release
tbb_link=`pwd`

mkdir -p /tbb/lib/
mv ${tbb_link}/* /tbb/lib/
mv ${tbb_dir}/include /tbb/
ls /tbb/lib/*
ls /tbb/include/*
cd ${cur_dir}


export MFLAG="-m64"
export CXXFLAGS=" ${MFLAG} -static-libstdc++"

pip install numpy==1.15.4 cmake==3.13.3




